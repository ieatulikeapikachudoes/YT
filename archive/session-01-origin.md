# Session 01: origin (2026-10-23 to 2026-11-01)

The session where the pipeline started. Deleted afterward; this is what it decided.

- Looked into HyperFrames (HeyGen, open source, HTML to MP4). Confirmed it renders in the cloud sandbox with the preinstalled headless Chrome.
- Voice: every hosted TTS is blocked from the sandbox. Kokoro (local, free) works; model files come from GitHub releases. Picked am_michael.
- Captions: transcription is blocked too, so voice is generated line by line and caption timing comes from that.
- Built the friend short (shorts/01-friend). v1 and v2 rendered; v2 posted to TikTok as a rough draft. Drafts in shorts/01-friend/history/.
- Wrote the pipeline + style brief into the Project, created this repo.
- Audited ffmpeg-skill (clean), parked it: Project doc claude/parked/ffmpeg-skill.md.
- Ground rule set here: on a research request, report findings and ask before installing or building anything.
