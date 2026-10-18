# Models, costs and prompting

This file covers WaveSpeed models and the prompting guide, which applies to every engine. For the Fish Audio engine's models, credits and tool cycle, see `fish-audio.md`.

## Contents
1. Default models per role
2. Verifying a model before use
3. Ballpark costs and the two paths
4. Plan files and `quote-plan`
5. Prompting guide (image, edit, video, lip-sync, voice)

## 1. Default models per role

Seedance 2.5 is the default video model for every clip. The other defaults are WaveSpeed's own recommended starting points as of October 2026. The catalog changes often, so confirm each model with `studio.py models` / `schema` (section 2).

| Role | Default model | Key inputs | Notes |
|---|---|---|---|
| Base portrait / master (text → image) | `bytedance/seedream-v5.0-pro` | `prompt`, `aspect_ratio`, `resolution` | Strong photorealism; a GPT Image model is a good alternative (`models gpt-image`) |
| References and keyframes (edit with reference) | `bytedance/seedream-v5.0-pro/edit` | `prompt`, `images: [url, ...]` | Pass the master (plus a reference) every time |
| **Clips (image → video): default** | `bytedance/seedance-2.5/image-to-video` | `prompt`, `image`, ... (check `schema`) | Best motion and identity hold; stored as `models.video` in every new project |
| Clips: cheaper alternative, only if the user agrees | `wavespeed-ai/minimax-h3/image-to-video` | `prompt`, `image`, `duration` | Much cheaper, generates native audio |
| Talking shots (lip-sync / talking avatar) | `wavespeed-ai/infinitetalk` | `image`, `audio`, `prompt` | Priced by audio length; keeps the locked voice |
| Voice (text → speech) | search: `models speech`, `models tts`, `-t text-to-audio` | varies | Choose by language and accent support |
| Longer single shot | `bytedance/seedance-2.5/video-extend` | `video`, `prompt` | Use sparingly |
| Video fix-ups | `bytedance/seedance-2.5/video-edit` | `video`, `prompt` | Repair or restyle one clip instead of re-generating it |

## 2. Verifying a model before use

1. `studio.py models <words>`: confirm the ID exists and see its type and base price. `all_types` in the output lists the catalog's type names for `-t`.
2. `studio.py schema <id>`: check the required inputs, the enums (aspect ratios, resolutions, durations), the defaults, and `price_drivers` (the inputs that change the price).
3. If a default has disappeared, search by role (`-t image-to-video`, `models lipsync`, `models avatar`) and pick a popular model of the same type. Record the choice with `set <slug> models.<role>=<id>`, so later episodes use the same models and the character looks the same.

Don't invent inputs. `run` rejects unknown input names before spending anything, and lists the accepted ones.

## 3. Ballpark costs and the two paths

Rough figures for presenting the plan before the API key works. Once it does, replace them with a live `quote-plan`.

| Item | Ballpark |
|---|---|
| One image (text → image or edit) | $0.03–0.05 |
| One 5s clip, Seedance 2.5 (default) | $0.50–1.50 |
| One 5s clip, MiniMax H3 (cheaper alternative) | $0.10–0.40 |
| Talking avatar | about $0.15 per started 5s of audio (60s ≈ $1.80) |
| One voice line | a few cents |

**Full path** for the first episode (about 15s, 4 shots, one talking shot): 8 portrait candidates, 6 references, 3 voice tests, 6 keyframes, 4 Seedance clips plus a re-roll, lip-sync, voice lines. **About $4–9.**

**Budget path**: 4 candidates, 3 references, one voice, 3 keyframes, 3 Seedance clips, and a voiceover instead of lip-sync. **About $2–5.** (With MiniMax H3 instead of Seedance it drops to about $1–2, but only offer that if the budget is tight.)

**Later episodes** reuse the master, references and voice, so they cost only keyframes, clips and lines: often half of the first episode.

## 4. Plan files and `quote-plan`

A plan lists the paid runs of one path or episode. `quote-plan` prices each item live and totals it. Items whose price depends on media that doesn't exist yet (for example the audio length for lip-sync) can carry a manual `unit_usd` estimate; the output marks them as estimates.

```json
{
  "plans": [
    {
      "name": "ep01-full",
      "items": [
        {"step": "production", "what": "keyframes", "model": "bytedance/seedream-v5.0-pro/edit",
         "inputs": {"prompt": "x"}, "count": 5},
        {"step": "production", "what": "clips 5s", "model": "bytedance/seedance-2.5/image-to-video",
         "inputs": {"duration": 5}, "count": 4},
        {"step": "production", "what": "lip-sync 8s", "model": "wavespeed-ai/infinitetalk",
         "unit_usd": 0.30, "count": 1}
      ]
    }
  ]
}
```

Fill `inputs` with the values that drive the price (duration, resolution, number of images); `schema` lists them under `price_drivers`. `assets/plan-template.json` has a full path and a budget path for a first episode.

## 5. Prompting guide

### Base portrait (the master, text → image)

The base portrait is the reference that every later image and clip copies the face from. Optimise it for a **clear, evenly lit, undistorted view of the face**, not for drama. Save the prompt as `prompts/base.txt`.

Recipe: labelled sections, in this order.

```text
Photorealistic, unedited smartphone photo taken by a friend standing about a metre away.
Scene: <a calm everyday place that fits the character>, <soft overcast daylight or open shade>, <2–3 ordinary background details>.
Subject: <Name>, a <age>-year-old <origin> <man/woman>, <IDENTITY BLOCK, word for word from the bible> and a calm, <vibe> expression.
Pose and framing: chest-up, eye level, facing the lens straight on, slightly off-centre, face filling about a third of the vertical frame, arms relaxed at the sides with hands out of frame. Mouth closed.
Wearing: <signature outfit; any hat pushed back so the forehead and brows are fully visible>.
Details: visible pores and fine lines, a few stray hairs, natural uneven skin tone, slightly creased clothes, ordinary background details.
Camera: typical phone main lens, mild smartphone HDR, deep focus with the background sharp, natural grain in the shadows, horizon very slightly tilted.
No text, no watermark, no logos. No beauty retouching, no studio lighting, no portrait-mode background blur.
```

Why each choice matters (use these as the "why it works" bullets):
- **Overcast light and straight-on, chest-up framing** give the model a clean, evenly lit view of the face. Every later scene copies the face from this image, so a clear reference matters more than drama.
- **Nothing covers the identity**: hats pushed back, no sunglasses, the hair off the brows. If the brows and eyes are half the identity, they must be fully visible.
- **"Taken by a friend", not "selfie"**: it avoids the wide-angle close-up distortion that makes noses huge, and it keeps the hands (a common failure point) out of frame.
- **Real-skin details and phone-camera flaws** (grain, mild HDR, a slightly tilted horizon) push the model away from glossy, plastic "AI faces". Words like "8k, masterpiece, hyperdetailed" push towards them, so leave them out.
- **Deep focus, no portrait blur**: the background stays readable for later edits, and the face edges stay clean.

Model choice: a strong photoreal text-to-image model, such as `bytedance/seedream-v5.0-pro` or a GPT Image model on WaveSpeed (`models gpt-image` to find the current ID and its `quality` / `size` options), or `seedream-5-0` / `gpt-image-2` on Fish Audio. Use 9:16 and high quality for this one image, because it is reused for everything. Generate 4 candidates and pick; picking is faster than describing.

### References and keyframes (edit with reference)

Always pass the master as the first image; add a matching reference when one exists (a full-body reference for a full-body shot). Start the prompt with the identity lock, then describe only what changes:

> Same man as in the reference image. Keep his face exactly identical: <identity block, word for word>. Keep the suit. Change: he is sitting on the green armchair holding a can of energy drink at arm's length, inspecting it with suspicion. Same living room, same warm window light. Vertical 9:16, candid smartphone photo.

Keyframes for clips that will be animated should leave room for the motion: a slight action pose, hands visible if they will move, and a clear head and mouth for talking shots.

### Video (image → video)

The keyframe already defines the look, so the prompt describes **motion only**: one subject action and one camera move, in the present tense.

> He slowly raises the can, sniffs it, and recoils slightly with a disgusted squint. Static camera, subtle handheld shake.

- One action per shot. Several actions in 5 seconds come out rushed and warped.
- Name the camera: static, slow push-in, slow pan left, handheld.
- Don't describe the face again; that invites drift. For ambient sound with native-audio models, add it at the end: "quiet room tone, clock ticking".
- Use 5s clips by default. Comedy timing usually comes from cutting between short shots, not from long shots.

### Lip-sync / talking avatar

- Keyframe: front or three-quarter view, face large in the frame, mouth closed or neutral, no hands in front of the face.
- Audio: a clean voice line without music. Pause briefly before the punchline; the talking model keeps the timing.
- Keep talking shots under about 8 seconds and cut away (reaction shot, prop insert) between lines.

### Voice

- Describe the voice in the bible's terms (age, accent, pace, energy), then keep the exact same settings for every line.
- Write lines for the ear: short sentences, punctuation for timing ("No. ... Absolutely not.").
- Generate one file per line, so lines can be re-timed in the edit without re-generating.
