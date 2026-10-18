# Fish Audio engine

Fish Audio is a Claude connector. When the user has connected it, its tools are available directly (`get_credit_balance`, `estimate_*`, `generate_*`, `text_to_speech`, and so on; often listed as `mcp__Fish_Audio__*`). It bills **credits** from the user's Fish plan. Free plans include a monthly allowance, so the first runs may cost the user nothing extra. No API key file is needed.

## Contents
1. Setup
2. The generation cycle
3. Models per role (October 2026)
4. Moving files in and out
5. Budget and bookkeeping
6. Gotchas

## 1. Setup

1. `get_credit_balance`: plan and remaining credits (`package_balance` + `package_extra_balance`).
2. `list_my_workspaces`: take the workspace id, which every estimate/generate call needs. Save it with `studio.py set <slug> fish.workspace_id=<id>`.
3. `list_media_models` (optionally `media_type=image|video`) shows what is available. Then call `get_media_model` **once per model you will use** and keep its `parameter_schema`, `required_roles` and `inputs` for the whole session. Don't call it again before every estimate; call it again only after an `invalid_arguments` error.

If the Fish Audio tools are missing, the user can connect Fish Audio under Settings → Connectors in the Claude app, or use WaveSpeed instead.

## 2. The generation cycle

The same cycle applies to images, edits and videos:

1. **Estimate**: `estimate_image_generation`, `estimate_image_edit` or `estimate_video_generation`, with exactly the parameters you plan to use. It is free and validates the request.
2. **Guard and approve**: `studio.py guard <slug> --credits <estimate>` (exit code 3 means the project's credit cap would be exceeded). Show the user the credits and get a yes. Approve per batch, for example "4 portraits, 2,400 credits, go?".
3. **Generate**: `generate_image`, `generate_image_edit` or `generate_video`, with the **same** parameters, plus `expected_credits` and `pricing_version` from the estimate, plus an `idempotency_key` (16–128 characters, unique per intended run, e.g. `<slug>-ep01-shot02-clip-1`). If a call errors or times out, retry with the **same** key: that way the run can never be charged twice.
4. **Wait**: submit independent generations in the same turn, then poll them together with `get_generation_status` (`generation_ids`, only the ones still running), waiting `poll_after_seconds` between calls (about 20s for images and 60s for videos). A finished status already contains the results.
5. **Save and log**: for each finished generation run
   `studio.py record --project <slug> --step <step> --engine fish --model <model_id> --id <generation_id> --credits <charged> --label <name> [-o <path template>] --view-url <view_url> <media.url ...>`.
   This downloads the files into the project and adds the credits to the ledger. Keep each result's `media.object_key`: it is the input for the next step (section 4).

If a tool result contains `_meta.tool_update`, tell the user about it and follow its guidance; don't resubmit automatically.

## 3. Models per role (October 2026)

Confirm with `list_media_models` / `get_media_model`; credit prices are the defaults reported by Fish and change with parameters.

| Role | Model | How | Credits (default) |
|---|---|---|---|
| Master portrait | `seedream-5-0` (t2i) | `parameters: {aspect_ratio: "9:16"}`, `count` up to 8 | about 600 each |
| Cheaper portraits / drafts | `gpt-image-2` (t2i) | | about 150 each |
| References and keyframes | `seedream-5-0` (edit) | `inputs: [{role: "ref", object_key: master}, ...]` (up to 14 refs), `aspect_ratio: "9:16"` | about 600 each |
| Alternative editor | `nano-banana` (edit) | strong at keeping a face from a reference | about 900 |
| **Video clips (default)** | `seedance-2.5`, i2v | `inputs: [{role: "startFrame", object_key: keyframe}]`, `parameters: {duration: "5s", resolution: "720p"}` | about 9,800 at 4s/480p; more for longer or higher resolution, so always estimate |
| Video from references | `seedance-2.5`, reference | `inputs: [{role: "ref", ...master and refs}]`, `parameters: {aspect_ratio: "9:16", ...}`; no keyframe needed | similar to i2v |
| Cheap video drafts | `seedance-2.0-mini` / `seedance-1-5-pro` | same roles as i2v | about 1,300 / 2,700 |
| Voice | `text_to_speech` + `search_voices` | section 6 | 1 credit per UTF-8 byte of text |
| Lip-sync on a finished clip (cheapest talking shot) | `veed/lipsync/lip-sync` | `inputs: [{role: "sourceVideo", ...clip}, {role: "sourceAudio", ...voice line}]`, no prompt | about 450 per second |
| Talking avatar from a still | `creatify/aurora-v2/avatar` | `inputs: [{role: "ref", ...keyframe}, {role: "sourceAudio", ...line}]` | about 1,940 per second |
| Premium talking avatar | `infinitalk/avatar` | same roles, prompt required | about 8,000 per second, rarely worth it |

Notes:
- `seedance-2.5` i2v has no `aspect_ratio` setting: the clip follows the start frame. Make every keyframe 9:16.
- `seedance-2.5` generates native audio (ambient sound). Spoken lines still come from the locked voice plus lip-sync, so the voice stays the same across episodes.
- `duration` is a string such as `"5s"`. Durations from 4s to 30s are allowed.
- 480p is fine for drafts. Use 720p for posting.

## 4. Moving files in and out

- **Reusing Fish results**: pass a finished result's `media.object_key` straight into the next estimate/generate call: master → edit → keyframe → video → lip-sync. Never download a result and upload it again. Save the important keys: `studio.py set <slug> fish.objects.master=<key> fish.objects.ref_front=<key>`. Later episodes then reuse them for free.
- **Uploading a local file** (a master made on WaveSpeed, the user's own photo, a voice line made elsewhere):
  1. `studio.py fileinfo <file>`: the exact `bytes` and the `content_type`.
  2. `create_media_upload` with the workspace id, `file_name`, `file_size` (exact bytes) and `content_type`.
  3. `studio.py put <file> <upload_url>`, adding `--header "Name: value"` for any headers the slot lists.
  4. Use the slot's `object_key` as the input.

  If the environment can't make HTTP uploads, give the user the `web_upload_url` to upload in the browser. Tell them which format the slot accepts.
- **Downloading**: `studio.py record` saves `media.url` files into the project. If the download is blocked, the result stays viewable at `view_url`; tell the user, and mention that allowing `*.fish.audio` in the app's network settings enables downloads.

## 5. Budget and bookkeeping

- Set a credit cap for the project at kickoff. By default use the credits the user is willing to spend, often the current free balance: `studio.py init ... --credit-cap N`, or later `studio.py budget <slug> --set-credits N`, but only when the user asks for a change.
- Run `guard` before every paid batch and `record` after every finished generation. `studio.py budget <slug>` then shows USD (WaveSpeed) and credits (Fish) side by side, per step.
- Credits are not dollars. When comparing engines, quote both: "this episode costs about 30,000 Fish credits or about $4 on WaveSpeed".
- When the credits run out halfway, offer to finish on WaveSpeed. The master and references are local files, so the character stays the same.

## 6. Gotchas

- **Voices**: browse with `search_voices` (`language` filter, e.g. `el` for Greek, `en`, `it`; prefer a high `task_count`). Test 2–3 voices with the same catchphrase and lock the `voice_id` in the bible and in `project.json` (`voice.engine=fish voice.id=...`). Use inline tags for delivery: `[pause]`, `[sighing]`, `[deadpan]`, `[chuckling]`, `[emphasis]`.
- **Voice cost**: 1 credit per UTF-8 **byte**. Latin letters are 1 byte; Greek and Cyrillic letters are 2. A 100-character Greek line costs about 200 credits. Free plans allow at most 500 bytes per call, so generate one line per call (that's the right granularity anyway).
- **Voice cloning** (`create_voice_clone`): only the user's own voice, or a voice whose owner has consented. Never a celebrity or a voice taken from someone's videos.
- Fish returns `disclaimers: ["synthetic_media"]` for lip-sync and avatars. Keep the AI-content label on when posting.
