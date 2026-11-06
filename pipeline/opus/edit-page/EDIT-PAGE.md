# Edit page (Simon's tap-to-edit layer on top of a video)

One private artifact per video. Template: `edit.html` (change only the `<title>` to "<Short name> Edit"). Capabilities: `{"db": {}, "assets": {}}`.
First page: Iran short, https://claude.ai/artifact/MQjWF8iepcLzikVLZUeKxg

## Data on each page (artifact db)
- `video/meta`: title, slug, kind ("factory" | "outside"), current (version number), duration,
  versions [{v, video: asset id, cover: asset id, note, date}],
  lines [{key, t, text}] (empty for outside videos), sound {ducking, hits [{id, label, on}]},
  cover {headline (use *stars* for red words), tag, frame}, copy {yt_title, yt_desc, tt_caption}.
- `edits/draft`: what Simon is editing right now (autosaved).
- `batches/<id>`: one per Send: {status "sent" | "applied", createdAt, from_version, summary,
  changes {lines {key: {text, mode "revoice"|"caption", was, t}}, sound {music_db, voice_db, ducking, hits {id: on}, note},
  cover {headline, tag, frame}, copy {...}, notes [{t, text}]}, result_version}.
- Revert is instant on the page: it sets `video/meta.current` to an older version. When applying the next batch, start from the version in `from_version`.

## New page for a factory video (do this at DELIVER)
1. Copy edit.html, set `<title>`, publish with capabilities db + assets.
2. Upload the phone mp4 and the cover as assets (Artifact publish, asset: true, file_paths).
3. Seed `video/meta` from timing.json (line keys/starts/text), the mix settings (hits), the cover text and the copy.
4. Send Simon the link with the video.

## Outside videos
Simon uploads on the page (20 MB cap), or Claude uploads a file Simon sends (asset upload + seed meta with kind "outside", lines []).
Possible edits: trim/cut, captions (transcribe with Parakeet), music/levels, text on screen, zooms, cover, copy. Re-voicing someone else's voice is not offered.

## When Simon texts "edits ready"
1. ArtifactData query `batches` where status == "sent" (oldest first).
2. Apply everything in one pass on the source (factory: script-A.json "say"/"text", re-voice only changed lines; mix settings; cover.py; template beats for notes. Vague notes: pick the fix yourself).
   Caption-only line edits: change `text` but keep the old `say` so the voice is untouched.
3. Rebuild, render.sh, check.py final. Copy-only batches need no render.
4. Upload the new phone mp4 + cover as assets; update `video/meta` (append version v+1, set current, update lines/sound/cover/copy); set the batch to status "applied" with result_version.
5. Send Simon the new video + pasted title/description/caption, and log the changes in the short's run.md. Repeated asks (e.g. louder music) go to lessons.md as proposed default changes.
