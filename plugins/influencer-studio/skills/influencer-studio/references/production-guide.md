# Production guide

Formats for step 4 (script and shot list), file layout for step 5, and the publish pack for step 6.

## Project layout

```
influencer-studio/<slug>/
  project.json            settings, chosen models, voice, current step (edit via `studio.py set`)
  ledger.jsonl            every paid run: model, cost, outputs (written by studio.py, don't edit)
  01-character/character-bible.md
  02-look/candidates…, master.png, refs/ref-front.png, ref-34.png, ref-full.png, ref-<expression>.png
  03-voice/voice.json, voice-test-*.mp3
  04-content/series.md, ep01-script.md, ep01-plan.json
  05-production/ep01/shot01-key.png, shot01-clip.mp4, line01.mp3, ...
  06-publish/ep01/captions.srt, final.mp4, cover.jpg, post.md
```

## Series sheet (`04-content/series.md`)

```markdown
# <Series name>
Format: <one sentence: what happens in every episode>
Length: <7–20s> · Shots: <3–5> · Talking: <yes/voiceover/silent>
Hook formula: "<e.g. Rating ___ as a 74-year-old>"
Sign-off: "<catchphrase or recurring last beat>"
Episode backlog:
1. <logline> | hook: "<first line or text on screen>"
2. ...
```

## Script and shot list (`04-content/epNN-script.md`)

```markdown
# EP01: <title>
Logline: <one sentence>
Hook (0–2s): <what we see + text on screen>
Payoff: <the last beat>
Target length: <seconds>

## Shots
### Shot 1 · 0:00–0:03 · <keyframe | clip | talking>
- Keyframe prompt (edit from master + ref-<x>): "Same man as in the reference image... Change: ..."
- Motion prompt: "<one action + one camera move>"
- Dialogue: "<line>" (or none)
- On-screen text: "<text>" (or none)
- Sound: <ambient / music cue / sfx>

### Shot 2 ...

## Lines (for TTS)
line01: "<text>"
line02: "<text>"
```

Write dialogue in the character's voice from the bible: their sentence length, their words, their worldview. Read every line aloud in your head. If it would work as a text post, it's probably too long for a 3-second shot.

## Production checklist (per shot)

1. Keyframe made from the master (+ reference), approved by the user.
2. Clip: image → video for action, talking avatar for dialogue to camera.
3. Look at the result before showing it: same face, hands and objects intact, no warped text, natural motion, mouth in sync. Re-roll once at most, then ask.
4. Record durations with `assemble.py --probe 05-production/ep01/*.mp4 05-production/ep01/*.mp3`.

## Captions (`06-publish/epNN/captions.srt`)

Standard SRT, timed to the real durations from `--probe`:

```
1
00:00:00,000 --> 00:00:01,800
Rating energy drinks.

2
00:00:01,800 --> 00:00:03,200
As a 74-year-old.
```

1–6 words per caption and at most two lines. Put the punchline in its own caption so it lands on the beat.

## Assembly

```bash
python3 <skill-dir>/scripts/assemble.py \
  --out 06-publish/ep01/final.mp4 \
  05-production/ep01/shot01-clip.mp4 05-production/ep01/shot02-clip.mp4 05-production/ep01/shot03-clip.mp4 \
  --voice 05-production/ep01/voiceover.mp3 \
  --srt 06-publish/ep01/captions.srt \
  --cover 06-publish/ep01/cover.jpg --cover-at 0.5
```

- Talking-avatar clips carry their own voice audio; leave `--voice` out for those and keep the clip audio.
- Voiceover over silent or ambient clips: pass `--voice`, and add `--mute-clips` if the clip audio competes with it.
- Stills (png/jpg) can be mixed in; each is held for `--still-seconds`.
- Music: `--music file --music-volume 0.1`. Trending sounds are better added in the platform app.
- Pick the cover frame (`--cover-at`) at the most absurd or expressive moment, ideally the hook frame.
- Check the result: extract a few frames, or watch it, before calling it done.

## Post pack (`06-publish/epNN/post.md`)

```markdown
# EP01: <title>
Video: final.mp4 · Cover: cover.jpg

## Caption options
1. <short, in character, ends with a question or verdict>
2. <alternative angle>
3. <shortest version>

## Hashtags (3–5)
#<niche> #<format> #<character name> #aicharacter

## First comment (pin it)
<in-character question that invites replies, e.g. "What should I rate next? Choose wisely.">

## Posting
Best time: <evening local time of the audience, e.g. 18:00–21:00> · Same video natively on TikTok, Reels, Shorts
Turn on: the platform's "AI-generated content" label
Reply to the first comments in character within the first hour.
```
