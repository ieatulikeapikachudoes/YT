# Handoff: making videos for Nothing Personal

## How the pipeline works ("the factory")
Code lives in Project files under `pipeline/factory/`. The cloud workspace (`/home/claude/np/factory/`) gets wiped, so rebuild from the Project files.
One command runs a whole batch with DeepSeek on Venice doing everything (no Claude needed): `bash run_batch.sh <batch-name> 5`
1. **Plan** (`orchestrate.py`): DeepSeek V4 Pro designs the batch as ONE experiment (one variable tested), picks 5 topics using `channel.md`, `lessons.md`, `results.json`.
2. **Script** (`chain.py`): write, 2 blind judge loops (changes auto-applied), fact check, hard cap 165 words. Structure: hook, open loop, body, payoff, end.
3. **Voice** (`voice.py`): Kokoro TTS, local and free. Parakeet recognizer times every word so animation lands on words. Use the `say` field for hard words.
4. **Storyboard** (`storyboard.py` + `kit/base.html`, `kit/styles.py`): DeepSeek writes JS that draws SVG scenes from kit helpers and GSAP beats timed with `WT(line, word)`. Snapshots (`snap.js`), 2 vision-judge loops (DeepSeek V4.1 Flash), then a free code check for tiny or empty frames and one cleanup pass.
5. **Package** (`package.py`): HyperFrames renders the 1080x1920 MP4, plus a clickbait cover and YouTube and TikTok titles and descriptions.
- Model choices: `routing.json`. Venice key: ask Simon (kept in a local `.env`, never in files).
- Cost: about $0.27 per short ($0.15 Venice plus about $0.12 Claude when run from a fresh session). Running from a long chat costs about 5x more.
- Extras on disk: HyperFrames registry (420 transitions, overlays, charts, maps, news tickers; index in `pipeline/factory/kit/registry-INDEX.md`), `music.py` (Venice music: ACE-Step $0.03, Lyria 3 Pro $0.10 a track). Neither is wired into the batch yet.

## Visual style rules
- Four styles: flat (Kurzgesagt-like), mono (black, white, one red), ink (white line art on black, ThatGuy-like), paper (black stick figures on off-white, one red).
- One idea per frame. Main subject 35 to 50 percent of frame height. Hook frame big and visible at 0s. Last frame never empty.
- Keep x 90 to 950 and y 260 to 1330. Captions sit at y 1380 to 1560, so nothing important goes there. Keep the bottom 330px and right 130px clear for app buttons.
- At most 2 short labels per frame. Never put the caption text on screen as a headline; show a picture instead.
- One accent color, spent on the thing that matters.
- No em dashes anywhere. Channel name never said.

## What's working
- Explainers that reveal a mechanism (batch 2: "friendship is unpaid labor" and "algorithms ghost you" were fine).
- Best channel results so far: Dan the AI agent (about 1.3k views) and "Why you don't have friends" (691). Both are pain or future stories, but hand-shaped with Simon.
- The DeepSeek-only run from a fresh context: 5 shorts for $1.33 total.

## What's not
- DeepSeek-written story shorts don't make sense ("recruiter", "man who traded friends"). For now make explainers with the factory; do stories by hand with Simon.
- Storyboards are still rough: clip-art feel, small subjects, judge only sees stills.
- Pronunciation slips (fixed "resume"; add new ones to `lessons.md`).
- Pure history or biography shorts did worst (Hoffer 12 views, Putin 77).

## Where we left off
- Batch 1 (5 shorts) is uploaded. Batch 2 (5 shorts) is rendered; Simon liked 2 of them.
- Music test: same Germany/Poland "hypothetical scenario" short rendered with ACE and with Lyria. Simon wants to give notes on it, and needs to pick a track to make music the default step.
- Next: Simon sends reference frames he likes; wire the best registry pieces (transitions, charts, news overlays) and Dan/Ramses custom parts into the kit; add music as a step; later try news-style and AI-avatar ad formats (Venice image plus audio to talking video, about $0.55 per 10s clip, untested).
- Standing rules: every render gets a cover plus YouTube and TikTok copy. Every upload attaches the cover. Never upload without approval. Findings only when asked to look into something. Ask before building.
