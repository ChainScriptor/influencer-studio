# Influencer Studio

A Claude skill that takes you from a rough idea to a recurring AI character and finished vertical videos for TikTok, Reels and Shorts. Claude runs the whole pipeline: it interviews you, keeps the character's face and voice consistent, writes the scripts, generates images and video on [WaveSpeed](https://wavespeed.ai) or through the [Fish Audio](https://fish.audio) connector (Seedance 2.5 by default on both), edits the final cut, and never spends more than the budget you set.

[Ελληνικά παρακάτω](#ελληνικά)

## What it does

| Step | What happens | Cost |
|---|---|---|
| Kickoff | Checks your WaveSpeed key and balance, opens or creates a project, sets a budget cap | free |
| 1. Character | Fresh viral examples, then three concept pitches or a menu-driven character builder (18 categories, from character type and build to hairstyle), then a Character Bible with a locked identity block | free |
| 2. Look | Master portrait, then a reference sheet that locks the face for every later shot | low |
| 3. Voice | Test 2–3 voices, lock one | low |
| 4. Content | Series format, episode ideas, script and shot list, live price quote | free |
| 5. Production | Keyframes, then Seedance 2.5 clips, voice lines and lip-sync | most of the spend |
| 6. Publish | Final 9:16 edit with burned-in captions, cover, captions and hashtags, cost report | free |

- **Budget guard:** every paid run is quoted first and needs your OK. The bundled script refuses to go past the cap.
- **Consistency:** every image and clip is generated from the same master portrait and references, so the character looks the same in every video.
- **Viral playbook:** hook rules, a format bank and script mechanics for AI characters are built in.
- **Character builder:** pick every detail from numbered menus (Average to Extreme, animal characters, build, face, eyes, features, facial hair, hair colour and style, accessories), or let Claude pitch concepts and fine-tune them.
- **Ready to post:** 1080×1920, -14 LUFS audio, captions placed outside the platform UI, cover frame, post copy.

## Requirements

- Claude with skills: the Claude desktop or web app (including Cowork), or Claude Code.
- At least one generation engine:
  - **Fish Audio** connector in Claude (Settings → Connectors). It uses your Fish plan's credits, including the free monthly ones, and needs no key file.
  - **WaveSpeed**: an account with an API key and some credit, https://wavespeed.ai/accesskey
- Python 3.8+ in Claude's environment (standard library only). ffmpeg for the final edit; if it's missing, the skill installs `imageio-ffmpeg`.

## Install

**Claude app (desktop / web / Cowork)**
1. Download [`influencer-studio.zip`](https://github.com/ChainScriptor/influencer-studio/raw/main/influencer-studio.zip).
2. Go to Settings → Capabilities → Skills → Upload skill and choose the zip. (The menu names can differ slightly between app versions.)

**Claude Code: as a plugin**
```
/plugin marketplace add ChainScriptor/influencer-studio
/plugin install influencer-studio@influencer-studio
```

**Claude Code: manually**
```bash
git clone https://github.com/ChainScriptor/influencer-studio
cp -r influencer-studio/plugins/influencer-studio/skills/influencer-studio ~/.claude/skills/
```

## Set up Fish Audio (optional, once)

Connect Fish Audio under Settings → Connectors in the Claude app. The skill checks your credits at the start, asks you for a credit cap, and logs every generation's credits in the project. If downloads are blocked, allow `*.fish.audio` in the app's network settings.

## Set up WaveSpeed (optional if you use Fish Audio, once)

1. Create an API key at https://wavespeed.ai/accesskey and add a few dollars of credit.
2. Save the key as a one-line text file named `wavespeed-key.txt` in the folder you work in with Claude. (A `WAVESPEED_API_KEY` environment variable, or `wavespeed login` from the WaveSpeed CLI, also work.)
3. Don't paste the key into the chat: it would stay in the conversation history.

If Claude reports a network error, allow `api.wavespeed.ai` (and the download domain named in the error) in your app's network settings.

## Use

Type `/influencer-studio`, or just say something like *"I want to create an AI influencer for TikTok"*. In Claude Code the plugin version may show up as `/influencer-studio:influencer-studio`.

Everything is saved in `influencer-studio/<project>/` inside your working folder:

```
01-character/character-bible.md
02-look/master.png, refs/
03-voice/
04-content/ep01-script.md, ep01-plan.json
05-production/ep01/
06-publish/ep01/final.mp4, cover.jpg, captions.srt, post.md
project.json, ledger.jsonl   (settings, and every paid run with its cost)
```

Come back any time and say "continue my influencer project": the skill picks up where you left off.

## Costs (rough)

The skill shows live WaveSpeed prices before anything is spent. As a ballpark for the first episode: **full path about $4–9**, **budget path about $2–5**. Later episodes reuse the character's look and voice, so they cost less. Prices and models change; the live quote is what counts.

## Responsible use

- Create fictional characters, or yourself or someone who has given consent. No celebrities, politicians or real private people.
- Turn on each platform's "AI-generated content" label.
- You are responsible for what you publish and for following each platform's rules.

## Repository layout

```
.claude-plugin/marketplace.json            Claude Code marketplace entry
plugins/influencer-studio/                 the plugin
  skills/influencer-studio/SKILL.md        the skill
    scripts/studio.py                      WaveSpeed client, projects, budget ledger
    scripts/assemble.py                    ffmpeg edit: 9:16, audio mix, captions, cover
    references/                            interview, viral patterns, models and costs, Fish Audio, production guide
    assets/                                Character Bible template, cost-plan template
influencer-studio.zip                      the same skill, ready to upload (rebuild with ./build-zip.sh)
```

Not affiliated with WaveSpeed or ByteDance.

---

## Ελληνικά

Skill για το Claude που φτιάχνει έναν viral AI χαρακτήρα και έτοιμα κάθετα βίντεο για TikTok, Reels και Shorts. Ακολουθεί 6 βήματα:

1. Χαρακτήρας και Character Bible
2. Εμφάνιση
3. Φωνή
4. Σενάρια
5. Παραγωγή με Seedance 2.5 στη WaveSpeed
6. Τελικό μοντάζ και κείμενα για δημοσίευση

Δουλεύει με τη WaveSpeed ή με το Fish Audio connector, που χρησιμοποιεί τα credits του λογαριασμού σας (και τα δωρεάν). Το skill δείχνει το κόστος πριν από κάθε πληρωμή και δεν ξεπερνά ποτέ το όριο budget που ορίζετε.

**Εγκατάσταση στην εφαρμογή Claude:**
1. Κατεβάστε το [`influencer-studio.zip`](https://github.com/ChainScriptor/influencer-studio/raw/main/influencer-studio.zip).
2. Ανεβάστε το στις Ρυθμίσεις → Capabilities → Skills → Upload skill.

**Claude Code:**
```
/plugin marketplace add ChainScriptor/influencer-studio
/plugin install influencer-studio@influencer-studio
```

**Ρύθμιση WaveSpeed:**
1. Φτιάξτε κλειδί στο https://wavespeed.ai/accesskey και βάλτε λίγο υπόλοιπο.
2. Αποθηκεύστε το κλειδί σε αρχείο `wavespeed-key.txt` μέσα στον φάκελο όπου δουλεύετε.
3. Μην επικολλήσετε το κλειδί στο chat.

**Χρήση:** γράψτε `/influencer-studio` ή απλά «θέλω να φτιάξω έναν AI influencer».

**Κόστος (περίπου):** $4–9 για το πρώτο επεισόδιο στην πλήρη διαδρομή, $2–5 στην οικονομική. Τα επόμενα επεισόδια κοστίζουν λιγότερο.

Άδεια χρήσης: MIT.
