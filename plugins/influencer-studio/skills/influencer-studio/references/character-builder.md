# Character builder

A menu-driven way to design the character's appearance, for users who want to choose every detail themselves. It can also be used after the concept pitch, to fine-tune the chosen concept. The output is the bible's **identity block** (and a few wardrobe lines).

## Contents
1. How to run it
2. Batch 1: Body and identity
3. Batch 2: Face
4. Batch 3: Hair and style
5. Prompt phrasing for the less obvious options
6. Rules: conflicts, limits, respect
7. From choices to the identity block

## 1. How to run it

Most categories have more options than a question tool can show (it allows about four), so show each batch as a **compact numbered menu in chat**:

- Every category gets a letter, and every option a number. The user answers with codes ("A3 B2 C3 F1 F4") or in words, and can say "you pick" for any category or the whole batch.
- Mark your recommended option with ★ where the concept or earlier answers suggest one.
- Multi-select categories say so ("pick any").
- Translate the labels into the user's language when it isn't English, and keep the letters and numbers.
- Anything left unanswered: choose what fits the concept and the vibe, and list what you chose in one line, so the user can correct it.
- Skip categories that don't apply (see the rules in section 6), and say which ones you skipped.

Example of how a batch looks in chat:

```text
1 · Body and identity (reply e.g. "A1 B2 C3 D3", or "you pick")
A. Character type: 1 Average ★ · 2 Bold · 3 Extreme · 4 Insect · 5 Frog · 6 Cat · 7 Dog · 8 Rodent · 9 Bird
B. Gender: 1 Female · 2 Male · 3 Trans man · 4 Trans woman · 5 Non-binary
...
```

After the three batches, write the identity block (section 7), show it, and continue with the lock gate from the interview guide.

## 2. Batch 1: Body and identity

**A. Character type**: 1. Average · 2. Bold · 3. Extreme · 4. Insect · 5. Frog · 6. Cat · 7. Dog · 8. Rodent · 9. Bird

**B. Gender**: 1. Female · 2. Male · 3. Trans man · 4. Trans woman · 5. Non-binary

**C. Age**: 1. Adult · 2. Mature · 3. Senior

**D. Ethnicity**: 1. African · 2. Asian · 3. European · 4. Indian · 5. Middle Eastern · 6. Mixed

**E. Skin color**: 1. Porcelain · 2. Fair · 3. Light · 4. Olive · 5. Tan · 6. Brown · 7. Deep brown · 8. Ebony

**F. Build**: 1. Slim · 2. Athletic · 3. Muscular · 4. Curvy · 5. Heavy · 6. Ultra Muscular · 7. Centaur

**G. Height**: 1. Average · 2. Tall · 3. Very tall

**H. Proportions** (pick any): 1. Long limbs · 2. Short legs · 3. Broad shoulders · 4. Tiny waist · 5. Egg body

## 3. Batch 2: Face

**I. Head shape**: 1. Oval · 2. Long · 3. Square · 4. High forehead · 5. Neanderthal · 6. Chiseled · 7. Pear · 8. Round · 9. Flat top · 10. Heart

**J. Neck**: 1. Average · 2. Thick · 3. Long · 4. Double chin

**K. Eye shape**: 1. Almond · 2. Round · 3. Monolid · 4. Deep set · 5. Downturned · 6. Hooded · 7. Upturned · 8. Wide / Anime · 9. Small · 10. Narrow · 11. Heavy lidded

**L. Eye color**: 1. Black · 2. Brown · 3. Hazel · 4. Green · 5. Blue · 6. Ice blue · 7. Amber · 8. Grey

**M. Features** (pick any): 1. Freckles · 2. Dimples · 3. Bags under eyes · 4. Eyeliner · 5. Cheekbones · 6. Full lips · 7. Thick eyebrows · 8. Beauty mark · 9. Large nose · 10. Bangs · 11. Sharp profile · 12. Beard · 13. Freckles & red hair · 14. Grey bun · 15. Angular jaw · 16. Unibrow · 17. Vintage waves · 18. Earrings · 19. Prominent ears · 20. Bald · 21. Gap teeth · 22. Glasses & buck teeth · 23. Dark makeup · 24. Thin face · 25. Receding hairline

**N. Facial hair**: 1. Clean · 2. Stubble · 3. Full beard · 4. Goatee · 5. Mustache · 6. Pencil mustache · 7. Walrus mustache · 8. Viking beard

**O. Distinctive features** (pick any): 1. Heterochromia · 2. Face tattoos · 3. Dark bob · 4. Pierced ear · 5. Eyebrow slit · 6. Bleached eyebrows · 7. Platinum hair · 8. Gold teeth · 9. Braces · 10. Scar on eyebrow · 11. Face gems · 12. Elf ears · 13. Dramatic makeup · 14. Nose bandage

## 4. Batch 3: Hair and style

**P. Hair color**: 1. Jet black · 2. Dark brown · 3. Chestnut · 4. Ginger · 5. Red · 6. Blonde · 7. Platinum · 8. Grey · 9. White · 10. Pastel pink · 11. Lilac · 12. Blue · 13. Green

**Q. Hairstyle**: 1. Straight bob · 2. Bald · 3. Buzz cut · 4. Bowl cut · 5. Mullet · 6. Braids · 7. Pigtails · 8. Afro · 9. Mohawk · 10. Voluminous waves · 11. Beehive · 12. Curly hair · 13. Long straight hair · 14. Short hair · 15. Devil horns · 16. Ice cream updo · 17. Ginger afro · 18. Space buns · 19. Bat wings hair · 20. Spiky hair · 21. Balding with sides · 22. Geometric stairs cut · 23. Asymmetric bob · 24. Twisted horns · 25. Side updo · 26. Mushroom cut

**R. Accessories** (pick any): 1. None · 2. Glasses · 3. Headphones · 4. Necklaces · 5. Baseball cap · 6. Handbag

## 5. Prompt phrasing for the less obvious options

Most options translate directly ("blonde hair", "hazel eyes", "goatee"). These need clearer wording, because image models take labels literally or ignore them:

| Option | Write in the prompt |
|---|---|
| Type: Average | realistic everyday proportions and features |
| Type: Bold | a believable human with one or two strikingly exaggerated features (the chosen ones), larger than life but still real |
| Type: Extreme | caricature-level exaggeration of the chosen features: oversized head or features, cartoonish proportions. Best in stylised 3D, or as a "hyperreal puppet / claymation-like" look |
| Type: Insect / Frog / Cat / Dog / Rodent / Bird | an anthropomorphic <species> character: the realistic head and face of a <species> (ask which one: pug, capybara, duck, mantis...) with human hair styling, human clothing and human posture, e.g. "a pug with a black bowl haircut, wearing a turtleneck" |
| Age: Adult / Mature / Senior | pick an exact age and use it everywhere: Adult 25–39, Mature 40–59, Senior 60+ (e.g. "a 72-year-old") |
| Build: Curvy | curvy, full-figured, with full hips |
| Build: Heavy | heavyset, with a large round belly |
| Build: Ultra Muscular | an exaggerated bodybuilder physique with huge arms and chest |
| Build: Centaur | a centaur: a human torso and head joined to the body of a horse (needs a fantasy setting; see the rules) |
| Height: Tall / Very tall | show it in relation to the surroundings: "towers over the doorway, has to duck under the door frame" |
| Proportions: Egg body | a rounded, egg-shaped torso with narrow shoulders and short limbs |
| Head: Neanderthal | a heavy brow ridge, a sloping forehead, a broad jaw |
| Head: Chiseled | sharply defined bone structure, a strong jawline and cheekbones |
| Head: Pear | a narrow forehead widening to a broad jaw and full jowls |
| Head: Flat top | a flat-topped skull, squared off on top |
| Head: Heart | a wide forehead tapering to a narrow pointed chin |
| Eyes: Wide / Anime | unusually large, wide-set eyes (photoreal) or anime-style eyes (stylised) |
| Eyes: Heavy lidded | heavy, half-closed eyelids, a sleepy look |
| Features: Cheekbones | high, prominent cheekbones |
| Features: Glasses & buck teeth | round glasses and prominent buck teeth |
| Features: Grey bun | grey hair pulled into a tight bun |
| Features: Vintage waves | 1940s-style finger waves |
| Distinctive: Heterochromia | heterochromia: one <colour> eye and one <colour> eye (fix which side is which) |
| Distinctive: Eyebrow slit | a shaved slit through the <left/right> eyebrow |
| Distinctive: Face gems | small adhesive face gems under the <left/right> eye |
| Distinctive: Nose bandage | a white adhesive bandage across the bridge of the nose |
| Hair: Devil horns / Twisted horns | hair sculpted and twisted into two horn shapes on top of the head |
| Hair: Ice cream updo | an updo swirled like a soft-serve ice cream cone |
| Hair: Bat wings hair | hair sculpted into two bat-wing shapes on either side of the head |
| Hair: Geometric stairs cut | a sharp geometric haircut with stepped, stair-like layers |
| Hair: Balding with sides | bald on top with a fringe of hair left on the sides |

## 6. Rules: conflicts, limits, respect

- **Positions are part of the identity.** For anything one-sided (a beauty mark, a scar on the eyebrow, a pierced ear, face tattoos, an eyebrow slit, heterochromia, face gems), fix the side and the spot ("a beauty mark just above the right corner of the lips") and keep that wording word for word.
- **How many marks**: for Average, 2–4 picks from features plus distinctive features plus facial hair keep a face memorable without turning it into a caricature. For Bold and Extreme types, up to about 6 is fine.
- **Resolve conflicts and say what you did**:
  - Bald (feature or hairstyle) means skip hair colour and hairstyle.
  - Clean facial hair overrides Beard.
  - "Freckles & red hair" sets the hair colour.
  - "Platinum hair" or "Dark bob" (distinctive) overrides the hair colour or hairstyle.
  - "Grey bun" and "Vintage waves" are hairstyles.
- **Animal types** (Insect, Frog, Cat, Dog, Rodent, Bird): ask for the species or breed. Skip ethnicity and skin colour. Use the hair-colour list for fur or feathers if wanted, and the head shape follows the animal. Hairstyles, accessories and clothing still apply, and they are what make the character funny.
- **Centaur and four-legged builds**: walking legs and hooves often morph in AI video. Prefer shots of the upper body, or standing still (see "AI feasibility" in `viral-patterns.md`), and say so when the user picks it.
- **Accessories** go into the wardrobe section, so they can change between episodes. If one is part of the identity (glasses worn in every clip), put it in the identity block instead.
- **Gender**: image models only see appearance, so describe the presentation explicitly, through the chosen features. For a trans or non-binary character, use the presentation the user wants, ask one short follow-up if it isn't clear, and record the character's gender and pronouns in the bible. Write the character with respect; their identity is never the joke.
- **Ethnicity**: broad labels produce generic faces, so offer to be more specific ("West African", "Korean", "Greek"). That also helps consistency. Exaggeration for Bold or Extreme types applies to the chosen hair, build, accessories and features, **never to ethnic traits**: no caricatures of ethnic features, even when asked.
- **Adults only**: every age option is an adult. Characters are fictional (see the boundaries in SKILL.md).

## 7. From choices to the identity block

Write the identity block in this order, as one dense English paragraph, face and body only:

**type and style → gender, exact age, ethnicity → skin → build, height, proportions → head shape and neck → eyes (shape, colour) → features and distinctive features with positions → facial hair → hair colour and hairstyle (or fur/feathers).**

Example (Bold, Male, Senior, European, Fair, Heavy, Average height, Egg body, Round head, Double chin, Hooded blue eyes, Thick eyebrows + Large nose + Prominent ears, Walrus mustache, White, Balding with sides):

> A larger-than-life 71-year-old European man with fair, ruddy skin, a heavyset build with a rounded egg-shaped torso, narrow shoulders and short limbs, average height. A round head with a double chin, hooded blue eyes under very thick, unruly white eyebrows, a large bulbous nose, and prominent ears that stick out. A huge white walrus moustache covering the upper lip. Bald on top, with a fringe of white hair on the sides.

Save the raw choices too. Add a "Builder choices" line to the bible (e.g. `A2 B2 C3 D3 E2 F5 ...`) and run `set <slug> character.builder="A2 B2 C3 ..."`, so a later session can show and adjust them.
