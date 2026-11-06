# Voice A/B: delivery markup (Nov 3 2026)

Question: does per-beat tone markup make the Gemini voice sound less like a teleprompter read?

Same script (Law 46 Weak Ties), same voice (Charon, tempo 1.08). Only the markup differs.
- A: `script-A.json`, no tone fields. voice.py uses the old pace cue per section paragraph.
- B: `script-B.json`, every line has a `tone`, short pauses and one sigh written in.

```bash
cd opus/shorts/law46
python3 ../../tools/voice.py proj-A Charon 1.08 script-A.json && python3 ../../tools/check.py voice . A
python3 ../../tools/voice.py proj-B Charon 1.08 script-B.json && python3 ../../tools/check.py voice . B
```
About $0.17 each. TTS is cached per paragraph, so re-runs after a tweak only pay for the changed lines.

Listen blind: rename `proj-A/assets/voice.wav` and `proj-B/assets/voice.wav` to X and Y in random order, play both, pick. Also watch for: any tone word spoken aloud (VOICE flag), length still 40 to 60 s, the fall sounding different from the gospel line.

Decision:
- B wins: keep the markup rule in the playbook (already written in) and voice all future shorts from marked-up scripts.
- A wins or no difference: delete the delivery markup bullet and the `tone` hard flag from the playbook. voice.py stays as is (a script with no tone fields behaves exactly like before).
- B wins but still flat inside a paragraph: rerun B with `VOICE_PER_LINE=1` and compare that too.

Result: (fill in)
