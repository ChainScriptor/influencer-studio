# Viral patterns for AI characters

A working playbook for short vertical video. Use it to shape the character in step 1 and the format and scripts in step 4. These are patterns, not guarantees: a strong character in a repeatable format, posted consistently, is what compounds.

## Contents
1. Why AI characters get shared
2. Hook rules (first 1–2 seconds)
3. Format bank
4. Script mechanics
5. Series and retention
6. Platform fit
7. Anti-patterns

## 1. Why AI characters get shared

- **Contrast / incongruity**: who the character is clashes with what they do. A 74-year-old Italian tailor reviewing energy drinks; a nun running a techno set; a medieval knight in a corporate stand-up. The gap is the joke, and it is clear in one frame without sound.
- **Deadpan sincerity**: the absurd premise is played completely straight. The character never winks at the camera, and the audience does the laughing.
- **Recognisable signature**: the same face, outfit, place and prop every time, so the character is recognised in the feed in under a second. This is also what makes AI generation consistent and cheap.
- **Specific point of view**: strong, slightly unreasonable opinions ("Pineapple belongs on pizza. In prison.") travel further than neutral information.
- **Outsider explaining the modern world**: a grandparent, a time traveller or an alien explains, rates or misunderstands current trends. There is endless material and it ties into trends.

## 2. Hook rules (first 1–2 seconds)

- Open on the most absurd frame of the video, not on an establishing shot.
- Start mid-action or mid-sentence. Never use an intro, logo or "hi guys".
- Put the hook in text on screen too, because many people scroll with the sound off.
- Hook formulas:
  - "Rating ___ as a ___-year-old" / "Day 37 of ___ trying ___"
  - A confident wrong statement: "Stairs are a scam. Let me explain."
  - A question the viewer wants answered: "What does 'rizz' mean? I asked my grandson. Mistake."
  - A pattern interrupt: something visually impossible happening calmly.
  - A stakes line: "If this works, I retire."

## 3. Format bank

| Format | Shape | Cost to produce |
|---|---|---|
| Rating / review | Character tries a thing, gives a verdict and a score | Low–medium: 3–4 shots, one talking shot |
| Explains the modern world | Reads or asks about a trend, misinterprets it with confidence | Low: talking head plus 1–2 cutaways |
| Terrible advice | Calm, confident, useless life advice | Low: a single talking shot can work |
| POV | "POV: your grandpa discovers ___", shot as if from the viewer's eyes | Medium |
| Day N of ___ | A recurring challenge with visible progress or decline | Medium; strong retention |
| Silent reaction | Expressions only, text on screen and music | Lowest: no voice, no lip-sync |
| Skill reveal | Unassuming character, then a sudden elite skill | Medium–high (action shots) |
| Mini story / lore | 3-part arcs with cliffhangers, a recurring cast of 1–2 | High; build the following first |
| Duet / stitch bait | Reacts to a common trend or sound, in character | Low–medium |
| Teach one thing | One word, recipe step or fact per episode, in character | Low; good for niche creators |

## 4. Script mechanics

- **Length**: 7–15 seconds for comedy, up to 30 seconds for teaching or story. Shorter gets rewatched.
- **Structure**: hook (0–2s), escalation (1–3 beats), payoff or button (the last line or look), optional sign-off. Cut everything that doesn't set up or pay off the joke.
- **Loop**: when the last line or frame leads back into the first, viewers rewatch without noticing. For example, the final line asks the opening question again.
- **Rule of one**: one idea per video, one action per shot, one joke per beat.
- **Comment bait**: end on a debatable verdict, a deliberately wrong score, or a direct question ("What should I rate next?"). Replies feed the next episodes.
- **Captions**: big, short, centred in the lower-middle area. Highlight the punchline word.

## 5. Series and retention

- Give the format a name and an episode count ("Nonno Rates the Internet #12"). Numbers signal "there's more" and invite a follow.
- Keep a running list of the comment requests and use them as episode ideas.
- Recurring elements build attachment: the catchphrase, the sign-off, the prop, a running gag (the cat that always walks through the shot, the neighbour off-screen).
- Post consistently: 3 or more per week beats occasional bursts. Batch-produce 3 episodes at once, because the master and references are reused, so each episode costs less than the first.

## 6. Platform fit

- 9:16 at 1080×1920, 30 fps, loudness around -14 LUFS (`assemble.py` does all of this).
- Safe zones: keep faces and captions out of the bottom ~20% (caption and buttons) and the right ~15% (like and share column).
- TikTok rewards rewatches and comments; Reels rewards shares and saves; Shorts rewards viewed vs swiped. The same video works on all three; post natively on each (no cross-platform watermarks).
- Use a trending sound at low volume under the voice when it fits. Add it in the platform app, since licensed sounds can't be baked into the file.
- Turn on the platform's AI-generated content label.

## 7. Anti-patterns

- A generic "beautiful AI influencer" with no bit: the market is saturated and it's hard to tell apart.
- Long lip-sync close-ups: the longer the talking shot, the more visible the artifacts. Cut away often.
- A face that changes between videos: viewers notice and stop trusting the character. Always generate from the master and the references.
- Slow openings, explaining the joke, too much text on screen.
- Copying a real person's likeness, voice or name.
