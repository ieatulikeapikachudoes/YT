# Opus Playbook v2: autonomous, start to finish (Nov 2026)

**Simon gives one instruction ("make a short", "make 3 shorts", "do chapter 46"). Opus runs every stage to a finished, checked package without asking him anything.**
Judges make the calls Simon used to make. He reviews only the finished videos. The ONE human gate left: nothing is uploaded or posted without his go-ahead.

No DeepSeek, no Venice text models. **Venice is used for ONE thing: the voice, Gemini 3.1 Flash TTS (Simon's pick, Nov 2 2026, the sole voice model).** Music stays off until Simon turns it on. Everything else in `opus/tools/` is free and local.
The Venice key lives only in a local `.env` (opus/tools/.env or the working directory). Never write it into Project files; if it's missing, ask Simon once.

---

## Architecture

```
ORDER ──> 1 PICK ──> 2 RESEARCH ──> 3 SCRIPT ──> 4 VOICE ──> 5 BOARD ──> 6 RENDER ──> 7 PACKAGE ──> DELIVER
            │            │             │            │           │            │             │
          gate         gate          gate         gate        gate         gate          (run.md)
```
Every stage follows the same loop:
1. **Make** the thing (best-of-N where it matters).
2. **Free checks** (code, `check.py`). Hard flags must be fixed before any judge sees it.
3. **Fresh judge** (Agent tool, a new agent that never saw the drafting; it gets only the brief below + the material).
4. **Keep best.** From round 2 on the judge compares old vs new blind (X/Y in random order). The winner survives. A newer version never wins just for being newer.
5. **Gate.** PASS = the judge says SHIP (or scores 8+/10) AND zero hard flags. Max 2 judge rounds per stage. If it still fails, take the best version, write the open issue in `run.md`, and keep going. Never stop to ask.

### Decision rules (these replace questions to Simon)
| Situation | Decision |
|---|---|
| Which chapter? | Score candidate chapters (universal pain, visual story, surprising law, solid research), pick the top N, log why. Skip chapters already made. |
| Which shape? | Load the `vonnegut-story-shapes` skill and match the shape to the chapter's law. Default Man in Hole. |
| Which hook? | Write 5 (none may reveal the turn), the hook judge ranks them, use #1. If the order says "hook test", render the best of each type (story, contrarian, pain question) as A/B/C. |
| Style / voice / length | flat style; voice is always Gemini 3.1 Flash "Charon" at tempo 1.08; 40 to 60 s (script 120 to 150 words incl. hook). |
| A claim has no solid source | Cut it or make it qualitative. Never stop. |
| The book says something the source doesn't | Use the source's version, log a "book note" in run.md. |
| Pronunciation flag | Respell in the "say" field, regenerate the voice, re-check. |
| A tool fails | Retry twice, then fix the code. If still blocked, finish the other shorts and report it. |
| Music | Off until Simon turns it on. Voice only (build.py copies voice.wav to mix.wav). |
| Upload / post | NEVER without Simon's go-ahead. Every upload attaches its cover. |

### The run log (`shorts/<slug>/run.md`)
Opus writes one line per decision as it goes: chapter pick and why, sources, hook ranking, each judge's score and verdict, which version won, every flag and how it was fixed, open issues, book notes, timings. This is how Simon sees what happened without being asked anything.

---

## Stages

### 0. Setup (fresh workspace)
Rebuild from the Project folder `pipeline/opus/` (kit, tools, shorts), run `bash opus/tools/setup.sh`, export the printed line. Read `pipeline/factory/channel.md`, `lessons.md`, `results.json`, and the book (artifact link in channel.md).

### 1. PICK
Draft 10 to 15 chapter briefs: chapter number and law line, bottom line, the story beat (who, what they want, what goes wrong, what flips), Vonnegut shape, the pain a stranger feels. Score and keep the top N. Gate: none (a decision rule), but log it.

### 2. RESEARCH
Web search every claim (study, number, named person). Write `research.md` with URLs and the exact finding. Gate: every number or study in the chapter that the script might use is either sourced or marked "do not use".

### 3. SCRIPT
- **Load the `vonnegut-story-shapes` skill first.** Pick the shape from the chapter's law (comeback -> Man in Hole or Cinderella; betrayal or loss -> Icarus / Old Testament; warning -> From Bad to Worse or Oedipus; hidden luck vs skill -> Which Way Is Up?; how something got built -> Creation Story). Plot every beat on the fortune line before writing. 120 to 150 words with the hook (Gemini reads about 2.6 words/s with the pace cue and tempo 1.08).
- **Story first, lesson second.** The story completes its own arc and the twist happens INSIDE the story. Then the preacher explains why it happened. Split: about two-thirds story, one-third lesson; "Here is the gospel" starts at 60% of the runtime or later, and the lesson runs about 18 s max.
- **Plant the turn.** Whoever or whatever causes the twist appears in the first third as harmless background, one beat the viewer barely notices.
- **Scenes, not summaries.** The fall and the turn each get one specific moment (a place, a time of day, a line of dialogue). At most one montage line of facts.
- **Lesson rules.** One proof at most (one study or number), and it must explain the story just told. The lesson calls back to the story's characters by name or role ("bench guy"), then ends on the book's bottom line.
- Add Gemini tags in the "say" field where the emotion turns: e.g. `[sadly]` at the fall, `[excitedly] Here is the gospel!`, `[shouting]` on the last line, `[short pause]` before a reveal. Tags are stripped for captions and timing.
- Write 5 hooks (at least one story, one contrarian law, one pain question). Each opens on the pain or a question and NEVER reveals who or what causes the turn. Test: if a stranger could guess the ending from the hook, it fails.
- In parallel: **hook judge** (H), **script judge** (S), **stranger test** (STRANGER). Revise. Then **side-by-side** (S-PAIR) on old vs new.
- Hard flags (fix before judging): em or en dashes, channel name, over 150 words, a claim not in research.md, more than one study or number in the lesson, a hook that names the turn.
- Gate: S-PAIR winner says SHIP, the stranger's one-sentence point matches the law, AND the stranger could NOT guess the ending from the first line. After the voice step, `check.py voice` flags LESSON EARLY if "Here is the gospel" starts before 60% of the runtime: cut lesson words or add story, then re-voice.

### 4. VOICE
`voice.py <dir>/proj-<V> Charon 1.08 <dir>/script-<V>.json` (Gemini 3.1 Flash via Venice; about $0.17 per short; every paragraph is cached in assets/tts so re-runs are free), then `check.py voice <dir> <V>`.
The tool adds a pace cue "[speaking quickly, with energy]" to every paragraph that doesn't start with its own tag (override with VOICE_PACE) and squeezes long pauses.
Gate: zero VOICE flags (a tag word in the transcript means a tag was spoken aloud: rewrite that tag) and a length of 40 to 60 s (tempo 1.0 to 1.15, or cut a line).

### 5. BOARD (Opus draws by hand)
- Write `scenes.js` + `beats.js` on the kit (`opus/kit/kit.html`; `opus/shorts/law31/` is the reference). Draw 2 versions of the hook frame.
- `build.py`, then `check.py board`. Hard flags: EMPTY, SMALL, STATIC (over 3 s with nothing moving), JS ERROR, TIMING.
- **Board judge** (B) on `check-<V>/board.jpg`; it also picks the hook frame. Apply, rebuild, re-check, then **B-PAIR**.
- Gate: B-PAIR winner says SHIP (or 8+/10) and zero hard flags.

### 6. RENDER
`render.sh <dir> <V> <out>`: a phone-sized mp4 (about 6 MB), then `check.py final` runs automatically.
Hard flags: STATIC, BLACK, blank last frame, audio too quiet or loud, clipping, silence over 1.2 s, length.
Gate: zero hard flags.

### 7. PACKAGE
- Cover: write 3 headline options, render the best 2 with `cover.py`; the **final judge** (F) sees the contact sheet + both covers, picks the cover, and flags video problems. Fix real flags only (re-render once at most).
- Copy: YouTube title (under 60 chars, keyword first), description (keyword in line 1, ends with a question, then #Shorts + 3 to 4 tags), TikTok caption (keyword first, one question, 3 to 5 tags). No em dashes.
- Log the short in results.json with empty slots for hold_3s / avg_pct_viewed / views.
- Save the short's source files (script, scenes.js, beats.js, short.json, research.md, run.md) to the Project under `pipeline/opus/shorts/<slug>/`.

### DELIVER
**Always paste the YouTube title + description and the TikTok caption right in the delivery message (ready to copy), not only in a file (Simon, Nov 4 2026).**
Copy rules that work on each platform:
- YouTube Shorts: title under 60 chars, the search keyword in the first 3 words (e.g. Iran, Trump), a question or open loop that matches the cover. Description: the first line repeats the keyword and the hook (it shows in search), 2 to 3 short lines on what the video shows, one comment question, then 3 hashtags (YouTube shows the first 3 above the title; skip #Shorts).
- TikTok: TikTok search reads the caption, so put the keyword phrase first. Use the hook line, one line of context, a comment question, then 3 to 5 hashtags mixing broad (#trump) and niche (#straitofhormuz). Keep it under about 150 chars before the hashtags.
- No em dashes. Label hypotheticals as hypothetical.
Make the video its own edit page (see `edit-page/EDIT-PAGE.md`) and include the link. When Simon texts "edits ready", follow that file.
Send Simon in one message: the mp4(s), the cover(s), the copy, and a 5-line summary from run.md (chapter, hook, judge scores, anything left open, book notes). Plus a `lessons-proposal.md` (up to 5 rules to add, up to 5 to delete, each tied to a specific flag or judge note). Lessons only change when he approves; this never blocks the run.

---

## Judge briefs (paste as the fresh agent's whole prompt, plus the material; tell it "no tools", give a word limit)

**H (hooks):** You are judging opening lines for a 50 second vertical story short. A stranger is scrolling. For each hook: would they stop in the first second? Does it open on pain or a question instead of setup? Clear with zero context? DOES IT GIVE AWAY THE ENDING or who causes the turn (if yes, rank it last)? Rank all 5, best first, one line of reason each. Name the best of each type (story, contrarian law, pain question). Optionally give one tighter version of the winner (12 words max, no em dashes).

**S (script, round 1):** You did not write this script and have no stake in it. Shape intended: <shape> (fortune line: <line>). Law it must land: <law line>. Bottom line to end on: <bottom line>. Sources: <research.md facts>. Hard rules: <word cap incl. hook>, no em dashes, plain words, preacher is fired up never deadpan. Check, and say PASS/FAIL for each of these five first: (1) the hook does not reveal the turn; (2) the character or thing that causes the turn is planted in the first third; (3) the story completes its own arc before "Here is the gospel" and the lesson is about a third of the script or less; (4) the fall and the turn each have one real scene (place, time, dialogue), not a list; (5) the lesson uses one proof at most and calls back to the story's characters. Then: does the fortune line match the shape with a big enough swing; every line drawable; each claim exactly matches the sources; logic jumps; tone; quotable line; likely top comment objection. Any FAIL on the five means VERDICT FIX or REWRITE. Output: the five PASS/FAIL lines, VERDICT (SHIP / FIX / REWRITE), SCORE /10, at most 8 numbered change requests with exact replacement wording.

**S-PAIR:** Two versions of the same script, X and Y (plus the sources and rules). Pick the one a stranger would watch to the end and remember, that breaks no rule. WINNER, one sentence why, then VERDICT for the winner: SHIP or at most 4 change requests with exact wording.

**STRANGER:** First read ONLY the first line and answer: how do you think this ends? Then read the whole script once, as someone who has never heard of the channel or the book. One sentence: the point. One sentence: what happened. Where did your interest dip? What confused you?

**B (board):** Contact sheet, one frame per spoken line, caption under each (plus 2 versions of the hook frame, labeled). Judge as a stranger on a phone for one second, then as an art director: one idea per frame; subject 35 to 50% of frame height; does each picture show its line's idea (name a sharper picture if one exists); consistent characters; color on what matters; nothing important under the captions, in the bottom 330 px or right 130 px; broken or overlapping shapes. Pick the hook frame. Output: SCORE /10, VERDICT, at most 10 numbered change requests naming the frame label and the exact change.

**B-PAIR:** Two contact sheets of the same storyboard, X and Y. Which reads clearer and looks more crafted on a phone? WINNER, one sentence why, VERDICT (SHIP or at most 5 change requests).

**F (final):** A contact sheet of a finished short (one frame per second) plus 2 cover options. Flag only real problems: a caption covering something important, a broken-looking cut, an unfinished frame, cut-off text. Pick the cover a stranger would tap. Output: COVER (1 or 2), then PASS or a numbered list of the second and the fix.

---

## Cost control
- About 7 judge agents per short (H, S, STRANGER, S-PAIR, B, B-PAIR, F). Each gets only its brief and the material.
- One board snap per round. Render only after the board gate. Re-render at most once, only for real final-judge flags.
- Deliver phone-sized mp4s (crf 21); delete raw renders.
