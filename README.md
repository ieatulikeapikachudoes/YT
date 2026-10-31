# Nothing Personal

Faceless YouTube channel. One stick figure explains how the world actually is. This repo is the production pipeline: script in, vertical MP4 with voice out.

The thinking (style brief, reference teardowns, scripts in progress) lives in the Claude Project. This repo is the code and the finished shorts.

## Layout

```
pipeline/          shared scripts
  make_voice.py    script.json -> voice.wav + per-line timings (Kokoro, local TTS)
  build.py         template.html + timings -> project/index.html
  venice.py        Venice AI client (OpenAI-compatible, GLM 5.2); key from .env
  setup.sh         one-time install (hyperframes, gsap, kokoro, model files)
docs/
  style-brief.md   what is fixed, what the style agent decides
shorts/
  01-friend/       one folder per short
    script.json    the lines: [key, text, pause_after]
    template.html  the composition; every animation keyed to T.<key>
    project/       the HyperFrames project (index.html is generated; voice.wav is not committed)
    renders/       published versions
```

## Setup

Copy `.env.example` to `.env` and add `VENICE_API_KEY`. `.env` is gitignored. Then `python3 pipeline/venice.py` to confirm the API works.

## Make a short

```bash
bash pipeline/setup.sh            # once per machine; then export the lines it prints
python3 pipeline/make_voice.py shorts/01-friend          # voice + timings; listen to project/assets/voice.wav
python3 pipeline/build.py shorts/01-friend               # writes project/index.html
cd shorts/01-friend/project
npx hyperframes lint
npx hyperframes snapshot --at 2,10,20,30,45,58            # look at the contact sheet before rendering
npx hyperframes render --output ../renders/v3.mp4
```

A new short: copy `shorts/01-friend` to `shorts/02-<name>`, rewrite `script.json`, rewrite the scenes in `template.html`, update the scene bounds in `pipeline/build.py` (or add a `scenes.json` next to the template).

## How it works

- HyperFrames (HeyGen, Apache 2.0): the video is HTML. Headless Chrome captures each frame, ffmpeg encodes. 1080x1920, 30fps, H.264.
- Kokoro generates the voice one line at a time, so each line's start time is exact. Captions and all scene timing come from that. No transcription step.
- The character is one SVG on a persistent layer that walks between scenes. His arm and head rotate with GSAP `svgOrigin`.
- Scenes are `.clip` divs with `data-start`/`data-duration`; `build.py` fills those from line keys so retiming the script retimes the video.

## Voices

Kokoro `am_michael` for v1 and v2. Other older-male options: `bm_george`, `bm_lewis` (British), `am_onyx` (deep). Upgrade path is ElevenLabs: generate on their site, drop the MP3 in as `voice.wav`, and supply a transcript for timings.

## Gotchas

- Rotating SVG parts: GSAP `svgOrigin: "x y"` in viewBox units, not CSS transform-origin.
- Captions: full-frame container, each caption pinned with `bottom`.
- Keep `template.html` outside `project/`; lint treats any root HTML with a composition id as an entry point.
- CDN scripts are blocked in the cloud sandbox: GSAP is vendored into `project/vendor/`.
- Lint warnings about "nested structure" and "dense track" are about Studio editing, not rendering.

## Status

- `shorts/01-friend`: v2 published to TikTok 2026-10-24 as a rough draft. Style pass pending (see docs/style-brief.md).
