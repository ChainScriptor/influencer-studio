# Character interview

The goal is a character that (a) stops the scroll, (b) can carry a repeatable series, and (c) can be generated consistently. Run the interview in batches of up to four questions, each with 2–4 options and the recommended one first. Derive the options from earlier answers, from `trend-notes.md` and from `viral-patterns.md`. Don't copy the examples below verbatim when the context points elsewhere.

How to pick the "(Recommended)" option: prefer the option with the strongest **contrast** that is also **easy to keep consistent and to animate**. A distinctive face, one signature outfit, one home location, one prop, and slow or arm-only motion are easy. Crowds, constantly changing outfits, fast full-body action and hands handling small objects are hard and expensive (see "AI feasibility" in `viral-patterns.md`).

The flow: **batch A → three concept cards → the user picks → batch B → batch C → bible → lock gate.** In builder mode (see `character-builder.md`), the builder's menus replace "who are they?" in batch A, the concept cards, and the face and hair questions of batch B. In "both" mode, the builder comes right after the user picks a concept.

## Batch A: the core (always ask)

1. **What's the goal for this character?**
   - Viral character: entertainment, follower growth (Recommended for a first project)
   - Niche creator who teaches or reviews something (cooking, tech, fitness, finance tips)
   - Brand mascot for a product or business
   - Storyteller with an ongoing plot or lore
2. **Who are they?** (gender, rough age, where from)
   Offer three combinations that create contrast with the goal. For a viral character, for example: "Man, 60s–70s, European" (Recommended: older characters doing unexpected things is a proven contrast engine) / "Woman, 80s, Southern US" / "Man, 30s, medieval knight out of time".
3. **What should make people stop scrolling?**
   - Contrast: who they are clashes with what they do (Recommended)
   - Absurd situation played completely straight
   - Extreme skill, or extreme incompetence
   - Relatable pain, said out loud
4. **Vibe in three words?** (pick one or type your own)
   - Deadpan, stylish, absurd (Recommended for contrast characters)
   - Warm, chaotic, wholesome
   - Smug, sharp, unbothered
   - Dramatic, theatrical, sincere

## Concept cards (after batch A)

Open with one line on the trend notes and one line restating the brief. Then pitch three concepts that are genuinely different from each other: a different job, a different signature action, a different risk profile. Use this format:

```markdown
**1. <Full name>, "<series nickname>"** ⭐ my pick
- **Concept:** <age, origin, former life> who <the repeatable action>, played <vibe>.
- **Signature look:** <two or three visual hooks that read at thumbnail size>.
- **Attitude:** <how they carry themselves; what they never do (e.g. never look at the camera)>.
- **Format:** <what happens in every clip, length, talking or wordless, and why it travels across languages>.
- **Why it works:** <the viral pattern it borrows (cite a trend-notes case when one applies), the series hook ("where is he conducting now?"), and the production risk, honestly: "fast motion is harder for video models, so stunts can morph">.
```

Then close with: "My recommendation is **<name>**. <One or two sentences: strongest repeatable format, and motion the video model handles well.>"

What makes a concept strong:
- The action is **repeatable in endless locations or variations**: that's the series.
- It works **without sound or language** where possible (wordless formats travel worldwide), or the audio *is* the joke.
- The motion suits AI video: arms, head turns, facial reactions and slow walks are safe; flips, stunts, running and object juggling are risky.
- The look has **two or three thumbnail-size hooks**: a hair shape, one garment, one accessory.

## Batch B: details of the chosen concept

Offer options specific to the chosen concept. These examples are for an older man:

1. **Face extras** (multi-select: "pick any, or I fill in the rest")
   - Ruddy, weathered cheeks (Recommended): outdoor skin, sun spots, deep crow's feet
   - Bushy white eyebrows: thick, slightly unruly, adds to the deadpan
   - Broken-nose bump: a slightly crooked nose from a "past life"
   - Small scar: faint, through the chin or an eyebrow

   Other good identity marks: a mole in a fixed spot, a gap tooth, hooded eyes, uneven brows, freckles, age spots. Two to four marks make a face memorable and help the model keep it the same. More than that turns into a caricature.
2. **Hair and facial hair**: three options that fit (for example a walrus moustache, a white pompadour, a bald crown with a white fringe).
3. **Signature outfit and prop**: three bundles. Keep them separate from the face in the bible. If the user wants to choose piece by piece, open the wardrobe and setting menus (batches 4–5 in `character-builder.md`).
4. **Backstory?**
   - One-line mystery (Recommended): "Retired alpine postman from a village near Garmisch. Nobody knows where he learned this." It fuels the comments.
   - Fuller story: a few lines with heart (widower, took up skating at 70 after his grandson dared him). Better for a lifestyle angle.
   - None: pure image, no lore.

If the character talks, add: **voice and language** (accent, energy; the default is the user's language, or English for international reach).

## Batch C: format and boundaries (can be one batch with defaults)

1. **Visual style**: photoreal, as if filmed on a phone (Recommended) / cinematic photoreal / stylised 3D / anime.
2. **Talking**: speaks to camera / voiceover only / silent (Recommended for wordless formats: cheapest and travels best).
3. **Off-limits topics**: politics, religion, swearing, anything the user wants to avoid (default: keep it brand-safe).
4. **Posting rhythm** for planning: 3/week (Recommended) / daily / weekly.

## Turning the answers into the bible

- **Concept line**: "<Name>, a <age> <origin> <identity> who <recurring action>, delivered <vibe>."
- **Identity block** (in English, one dense paragraph, face and body only): face shape, eyes (colour and shape), brows, nose, mouth and teeth if visible, the chosen marks *with their exact positions* ("a small mole on the left cheekbone"), facial hair, hair (cut, colour, hairline), skin tone and texture, build and posture. No clothing, no setting, no mood. Avoid vague words like "handsome" or "stylish": describe what makes them look that way. This paragraph goes word for word into every image prompt.
- **Wardrobe and props**: the signature outfit down to colours and fabrics, the prop, alternates. Kept separate, so outfits can change while the face stays locked.
- **Home setting**: room or place, key furniture, colours, light.
- **Personality and voice**: how they talk (sentence length, favourite words, what they never say), their worldview, what annoys or delights them.
- **The bit**: catchphrase, sign-off, recurring gesture or prop moment.
- **Backstory**: from batch B.
- **Boundaries**: from batch C.

The template is in `assets/character-bible-template.md`.

## Lock gate

After writing the bible, summarise it in a few lines and ask one question: "Anything to change before we lock <name>?"
- **Lock it** (Recommended)
- Change the look
- Change the personality or format

After the lock, the identity block only changes if the user explicitly asks, because every image made afterwards depends on it.
