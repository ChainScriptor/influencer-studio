# Models, costs and prompting

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
| Master portrait (text → image) | `bytedance/seedream-v5.0-pro` | `prompt`, `aspect_ratio`, `resolution` | Strong photorealism |
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

### Master portrait (text → image)

Structure: **shot type and framing → who (Visual DNA) → wardrobe → expression and pose → setting → light → camera and texture.**

Photoreal "filmed on a phone" look: "candid smartphone photo, natural window light, slight grain, realistic skin texture with pores and wrinkles, unretouched, 9:16 vertical". Avoid "8k, masterpiece, hyperdetailed": those words push towards plastic, over-smooth faces.

Example:
> Vertical 9:16 medium close-up portrait. A 74-year-old Italian man with a long narrow face, deep-set brown eyes under thick salt-and-pepper eyebrows, a prominent Roman nose, deep forehead wrinkles, neatly trimmed white stubble, and silver hair combed straight back with a receding hairline. Slim, upright posture. Charcoal three-piece wool suit, burgundy silk tie, gold tie pin. Unimpressed deadpan expression, looking straight into the lens. 1970s living room with green velvet armchair and wood panelling, softly out of focus. Warm late-afternoon window light from the left. Candid smartphone photo, realistic skin texture, slight grain.

Generate several candidates (the `num_images` input, or several runs) rather than polishing one prompt endlessly. Picking is faster than describing.

### References and keyframes (edit with reference)

Always pass the master as the first image; add a matching reference when one exists (a full-body reference for a full-body shot). Start the prompt with the identity lock, then describe only what changes:

> Same man as in the reference image. Keep his face, age, hair, stubble and suit exactly identical. Change: he is sitting on the green armchair holding a can of energy drink at arm's length, inspecting it with suspicion. Same living room, same warm window light. Vertical 9:16, candid smartphone photo.

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
