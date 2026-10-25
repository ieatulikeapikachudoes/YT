"""Generate the voiceover for a short, one line at a time, and record when each line starts.

usage: python3 pipeline/make_voice.py shorts/01-friend [voice]

Reads  <short>/script.json   {"voice": "am_michael", "speed": 0.92, "lines": [[key, text, pause_after_seconds], ...]}
Writes <short>/project/assets/voice.wav
       <short>/project/assets/timing.json   per-line start/end
       <short>/project/assets/timing.js     window.__T (key -> start) and window.__LINES ([start, text]) for the template

Model files: set KOKORO_MODEL_DIR, default ./kokoro-model (see pipeline/setup.sh).
"""
import json, os, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

short = os.path.abspath(sys.argv[1])
script = json.load(open(f"{short}/script.json"))
voice = sys.argv[2] if len(sys.argv) > 2 else script.get("voice", "am_michael")
speed = script.get("speed", 0.92)
model_dir = os.environ.get("KOKORO_MODEL_DIR", os.path.abspath("kokoro-model"))
out = f"{short}/project/assets"
os.makedirs(out, exist_ok=True)

kokoro = Kokoro(f"{model_dir}/kokoro-v1.0.onnx", f"{model_dir}/voices-v1.0.bin")
lang = "en-gb" if voice.startswith("b") else "en-us"

LEAD = 0.3
sr = 24000
chunks = [np.zeros(int(LEAD * sr), dtype=np.float32)]
t = LEAD
timing = []
for key, text, gap in script["lines"]:
    samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    samples = samples.astype(np.float32)
    thr = 10 ** (-45 / 20)
    idx = np.where(np.abs(samples) > thr)[0]
    if len(idx):
        samples = samples[max(0, idx[0] - int(0.03 * sr)) : min(len(samples), idx[-1] + int(0.08 * sr))]
    dur = len(samples) / sr
    timing.append({"key": key, "text": text, "start": round(t, 3), "end": round(t + dur, 3)})
    chunks.append(samples)
    chunks.append(np.zeros(int(gap * sr), dtype=np.float32))
    t += dur + gap

audio = np.concatenate(chunks)
peak = np.max(np.abs(audio)) or 1.0
audio = audio / peak * 0.89
total = round(len(audio) / sr, 3)
sf.write(f"{out}/voice.wav", audio, sr)

T = {l["key"]: l["start"] for l in timing}
T["end"] = total
json.dump({"voice": voice, "total": total, "lines": timing}, open(f"{out}/timing.json", "w"), indent=1)
with open(f"{out}/timing.js", "w") as f:
    f.write("window.__T = " + json.dumps(T) + ";\n")
    f.write("window.__LINES = " + json.dumps([[l["start"], l["text"]] for l in timing]) + ";\n")

print(f"{voice}: total {total:.2f}s")
for l in timing:
    print(f"{l['start']:6.2f} {l['end']:6.2f}  {l['key']:9s} {l['text']}")
