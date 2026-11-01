"""Voice in paragraphs (smooth prosody), per-line timing recovered with the speech recognizer."""
import json, sys, os, re
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
import sherpa_onnx

MODEL_DIR = "/home/claude/np/kokoro-model"
PROJ = sys.argv[1]
VOICE = sys.argv[2] if len(sys.argv) > 2 else "am_michael"
SPEED = float(sys.argv[3]) if len(sys.argv) > 3 else 0.92

SCRIPT = json.load(open(sys.argv[4]))
LINES = [(l["key"], l["text"]) for l in SCRIPT["lines"]]
SAY = {l["key"]: (l.get("say") or l["text"]) for l in SCRIPT["lines"]}
PARAS = []
for l in SCRIPT["lines"]:
    if PARAS and PARAS[-1][2] == l["sec"] and len(PARAS[-1][0]) < 3: PARAS[-1][0].append(l["key"])
    else: PARAS.append([[l["key"]], {"hook": 0.5, "loop": 0.6, "body": 0.45, "payoff": 0.55, "end": 1.0}.get(l["sec"], 0.5), l["sec"]])
PARAS = [(k, g) for k, g, _ in PARAS]; PARAS[-1] = (PARAS[-1][0], 1.2)
FIX = []
TEXT = dict(LINES)

kokoro = Kokoro(f"{MODEL_DIR}/kokoro-v1.0.onnx", f"{MODEL_DIR}/voices-v1.0.bin")
M = "/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
        joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", num_threads=2, model_type="nemo_transducer")

NUM = {"two":"2","three":"3","four":"4","five":"5","seven":"7","fifteen":"15","forty":"40","twenty":"20","ninety":"90","six":"6","ten":"10","seventyfour":"74"}
def norm(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    return NUM.get(w, w)
def words_with_times(samples24):
    # resample 24k -> 16k
    n16 = int(len(samples24) * 16000 / 24000)
    x = np.interp(np.linspace(0, len(samples24) - 1, n16), np.arange(len(samples24)), samples24).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    toks, ts = s.result.tokens, s.result.timestamps
    words = []  # (word, start)
    for tok, t in zip(toks, ts):
        if tok.startswith(" ") or not words:
            words.append([tok.strip(), t])
        else:
            words[-1][0] += tok
    RAW.append([(re.sub(r"[^a-z0-9]", "", w.lower()), t) for w, t in words])
    return [(norm(w), t) for w, t in words if norm(w)]

RAW = []; WORDS = []
LEAD, sr = 0.3, 24000
chunks = [np.zeros(int(LEAD * sr), dtype=np.float32)]
t0, timing = LEAD, []
for keys, gap in PARAS:
    text = " ".join(SAY[k] for k in keys)
    ph = kokoro.tokenizer.phonemize(text, "en-us")
    for x, y in FIX: ph = ph.replace(x, y)
    samples, sr = kokoro.create(ph, voice=VOICE, speed=SPEED, lang="en-us", is_phonemes=True)
    samples = samples.astype(np.float32)
    idx = np.where(np.abs(samples) > 10 ** (-45 / 20))[0]
    samples = samples[max(0, idx[0] - int(0.03 * sr)): min(len(samples), idx[-1] + int(0.12 * sr))]
    dur = len(samples) / sr
    wt = words_with_times(samples)
    # locate each line's first two words in order
    pos = 0; starts = []
    for k in keys:
        lw = [norm(w) for w in SAY[k].replace("-"," ").split() if norm(w)]
        found = None
        for i in range(pos, len(wt)):
            if wt[i][0] == lw[0] and (len(lw) < 2 or i + 1 >= len(wt) or wt[i + 1][0] == lw[1] or wt[i + 1][0].startswith(lw[1][:3])):
                found = i; break
        if found is None:
            for i in range(pos, len(wt)):
                if wt[i][0].startswith(lw[0][:4]): found = i; break
        if found is None:
            print("ALIGN FALLBACK", k); starts.append(None)
        else:
            starts.append(wt[found][1]); pos = found + 1
    # fill None by proportion
    cum = 0; total_chars = sum(len(SAY[k]) for k in keys)
    for j, k in enumerate(keys):
        if starts[j] is None or (j and starts[j-1] is not None and starts[j] <= starts[j-1]): starts[j] = dur * cum / total_chars
        cum += len(SAY[k])
    for j, k in enumerate(keys):
        st = t0 + max(0.0, starts[j] - 0.05)
        en = t0 + (starts[j + 1] - 0.05 if j + 1 < len(keys) else dur)
        timing.append({"key": k, "text": TEXT[k], "start": round(st, 3), "end": round(en, 3)})
    WORDS.extend([[w, round(t0 + t, 3)] for w, t in RAW[-1] if w])
    chunks += [samples, np.zeros(int(gap * sr), dtype=np.float32)]
    t0 += dur + gap

audio = np.concatenate(chunks); audio = audio / (np.max(np.abs(audio)) or 1) * 0.89
total = round(len(audio) / sr, 3)
os.makedirs(f"{PROJ}/assets", exist_ok=True)
sf.write(f"{PROJ}/assets/voice.wav", audio, sr)
T = {l["key"]: l["start"] for l in timing}; T["end"] = total
E = {l["key"]: l["end"] for l in timing}
json.dump({"voice": VOICE, "speed": SPEED, "total": total, "lines": timing}, open(f"{PROJ}/assets/timing.json", "w"), indent=1)
with open(f"{PROJ}/assets/timing.js", "w") as f:
    f.write("window.__T = " + json.dumps(T) + ";\nwindow.__E = " + json.dumps(E) + ";\n")
    f.write("window.__W = " + json.dumps(WORDS) + ";\n")
    f.write("window.__LINES = " + json.dumps([[l["start"], l["text"], l["end"], l["key"]] for l in timing]) + ";\n")
print(f"total {total:.2f}s")
for l in timing: print(f"{l['start']:6.2f} {l['end']:6.2f}  {l['key']:7s} {l['text']}")
