"""Voice for Nothing Personal shorts: Gemini 3.1 Flash TTS (via Venice) is the ONLY voice model (Simon, Nov 2 2026).

usage: python3 voice.py <proj_dir> [voice=Charon] [tempo=1.0] <script.json>
  - Speaks the script in paragraphs (smooth prosody), one Venice call per paragraph, cached in <proj_dir>/assets/tts/
    so re-runs never pay twice for the same text.
  - Delivery markup (Nov 3 2026): each line may carry a "tone" field, a short spoken direction like "flat, tired" or
    "fired up". A paragraph is a run of consecutive lines with the same tone (max 3, same section). Each paragraph is
    sent to Gemini with the cue "[<tone>, keep a brisk pace]" so the delivery changes beat by beat instead of one voice
    for the whole script (VOICE_BRISK overrides the pace part). Lines with no tone get the old pace cue.
    VOICE_PER_LINE=1 forces one Venice call per line.
  - Inline Gemini tags are still allowed in a line's "say" field, e.g. "[short pause]" or "[sighs]". Tags are stripped
    for word timing and captions. With no tone, a paragraph whose text starts with its own tag keeps that tag and gets no cue.
  - tempo speeds the read up without changing pitch (ffmpeg atempo). Pauses over 0.35 s are squeezed to 0.3 s automatically; tempo 1.0 to 1.1 usually lands 40 to 60 s.
  - The local Parakeet recognizer times every word so the animation lands on words (writes timing.json / timing.js).
Needs VENICE_API_KEY in the environment or a .env next to this file or in the working directory (never stored in the Project)."""
import hashlib, json, os, re, subprocess, sys, urllib.error, urllib.request
import numpy as np
import soundfile as sf
import sherpa_onnx
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import costs  # pipeline/costs.py: token and cost log per short

MODEL = "tts-gemini-3-1-flash"
PROJ = sys.argv[1]
VOICE = sys.argv[2] if len(sys.argv) > 3 else "Charon"
TEMPO = float(sys.argv[3]) if len(sys.argv) > 4 else 1.0
SCRIPT = json.load(open(sys.argv[-1]))
SR = 24000

def key():
    if os.environ.get("VENICE_API_KEY"): return os.environ["VENICE_API_KEY"]
    T = os.path.dirname(os.path.abspath(__file__))
    for p in [os.path.join(T, ".env"), os.path.join(T, "..", "..", "..", ".env"), ".env", os.path.expanduser("~/.venice.env")]:  # tools/, repo root, cwd
        if os.path.exists(p):
            for l in open(p):
                if l.startswith("VENICE_API_KEY="): return l.split("=", 1)[1].strip()
    sys.exit("No VENICE_API_KEY (env var or .env). Ask Simon; never write it into Project files.")

TAG = re.compile(r"\[[^\]]*\]")
PACE = os.environ.get("VOICE_PACE", "speaking quickly, with energy")   # Gemini is slow (2.2 words/s); this cue makes it ~13% faster and is not spoken. Bare words, no brackets: the tool brackets it together with the line's tone.
PER_LINE = os.environ.get("VOICE_PER_LINE") == "1"
LINES = [(l["key"], l["text"]) for l in SCRIPT["lines"]]
SAY = {l["key"]: (l.get("say") or l["text"]) for l in SCRIPT["lines"]}
TONE = {l["key"]: (l.get("tone") or "").strip() for l in SCRIPT["lines"]}
PLAIN = {k: re.sub(r"\s+", " ", TAG.sub(" ", v)).strip() for k, v in SAY.items()}
GAP = {"hook": 0.4, "loop": 0.5, "body": 0.35, "payoff": 0.45, "end": 0.7}
PARAS = []   # [keys, gap, sec, tone]
for l in SCRIPT["lines"]:
    k, sec, tone = l["key"], l["sec"], TONE[l["key"]]
    same = PARAS and PARAS[-1][2] == sec and PARAS[-1][3] == tone and len(PARAS[-1][0]) < 3 and not PER_LINE
    if same: PARAS[-1][0].append(k)
    else: PARAS.append([[k], GAP.get(sec, 0.4), sec, tone])
PARAS = [(k, g, t) for k, g, _, t in PARAS]; PARAS[-1] = (PARAS[-1][0], 0.15, PARAS[-1][2])
TEXT = dict(LINES)

BRISK = os.environ.get("VOICE_BRISK", "keep a brisk pace")   # added after a line's tone so the pace holds without contradicting a quiet or tired tone
def cue(tone):
    if tone: return f"[{tone}, {BRISK}]" if BRISK else f"[{tone}]"
    return f"[{PACE.strip(' []')}]" if PACE.strip() else ""

def tts(text):
    os.makedirs(f"{PROJ}/assets/tts", exist_ok=True)
    h = hashlib.sha1(f"{MODEL}|{VOICE}|{text}".encode()).hexdigest()[:16]; mp3 = f"{PROJ}/assets/tts/{h}.mp3"
    if not os.path.exists(mp3):
        body = json.dumps({"model": MODEL, "input": text, "voice": VOICE, "response_format": "mp3"}).encode()
        req = urllib.request.Request("https://api.venice.ai/api/v1/audio/speech", data=body, headers={"Authorization": "Bearer " + key(), "Content-Type": "application/json"})
        for attempt in range(3):
            try: open(mp3, "wb").write(urllib.request.urlopen(req, timeout=180).read()); break
            except urllib.error.HTTPError as e:
                if attempt == 2: sys.exit(f"Venice TTS failed: {e.code} {e.read()[:300]}")
        costs.log("voice", MODEL, chars=len(text), short_dir=os.path.dirname(os.path.abspath(PROJ)), note="tts paragraph")
    else:
        costs.log("voice", MODEL, chars=0, short_dir=os.path.dirname(os.path.abspath(PROJ)), note="tts cache hit, free")
    af = f"atempo={TEMPO}," if abs(TEMPO - 1) > 1e-3 else ""
    # Gemini leaves long gaps inside paragraphs: squeeze any pause over 0.35 s down to 0.3 s (the words themselves are untouched)
    sq = "silenceremove=start_periods=0:stop_periods=-1:stop_duration=0.35:stop_threshold=-42dB:stop_silence=0.3,"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-af", f"{sq}{af}aresample={SR}", "-ac", "1", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

M = os.environ.get("PARAKEET_DIR", "/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8")
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
        joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", num_threads=2, model_type="nemo_transducer")
NUM = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "ten": "10", "fifteen": "15", "twenty": "20", "forty": "40", "ninety": "90"}
def norm(w): w = re.sub(r"[^a-z0-9]", "", w.lower()); return NUM.get(w, w)
RAW = []
def words_with_times(x):
    n16 = int(len(x) * 16000 / SR); y = np.interp(np.linspace(0, len(x) - 1, n16), np.arange(len(x)), x).astype(np.float32)
    words = []
    for o in range(0, len(y), 16000 * 20):                       # 20 s windows keep the recognizer accurate on long paragraphs
        s = rec.create_stream(); s.accept_waveform(16000, y[o:o + 16000 * 20]); rec.decode_stream(s)
        for tok, t in zip(s.result.tokens, s.result.timestamps):
            if tok.startswith(" ") or not words: words.append([tok.strip(), t + o / 16000])
            else: words[-1][0] += tok
    RAW.append([(re.sub(r"[^a-z0-9]", "", w.lower()), t) for w, t in words])
    return [(norm(w), t) for w, t in words if norm(w)]

WORDS = []; LEAD = 0.15
chunks = [np.zeros(int(LEAD * SR), dtype=np.float32)]; t0, timing = LEAD, []
for keys, gap, tone in PARAS:
    para = " ".join(SAY[k] for k in keys)
    c = cue(tone)
    # a tone cue always leads the paragraph; without a tone, a paragraph that starts with its own tag keeps just that tag
    x = tts(para if not c or (not tone and para.lstrip().startswith("[")) else f"{c} {para}")
    idx = np.where(np.abs(x) > 10 ** (-45 / 20))[0]
    x = x[max(0, idx[0] - int(0.03 * SR)): min(len(x), idx[-1] + int(0.12 * SR))]
    dur = len(x) / SR; wt = words_with_times(x); pos = 0; starts = []
    for k in keys:
        lw = [norm(w) for w in PLAIN[k].replace("-", " ").split() if norm(w)]; found = None
        for i in range(pos, len(wt)):
            if wt[i][0] == lw[0] and (len(lw) < 2 or i + 1 >= len(wt) or wt[i + 1][0] == lw[1] or wt[i + 1][0].startswith(lw[1][:3])): found = i; break
        if found is None:
            for i in range(pos, len(wt)):
                if wt[i][0].startswith(lw[0][:4]): found = i; break
        if found is None: print("ALIGN FALLBACK", k); starts.append(None)
        else: starts.append(wt[found][1]); pos = found + 1
    cum = 0; total_chars = sum(len(PLAIN[k]) for k in keys)
    for j, k in enumerate(keys):
        if starts[j] is None or (j and starts[j - 1] is not None and starts[j] <= starts[j - 1]): starts[j] = dur * cum / total_chars
        cum += len(PLAIN[k])
    for j, k in enumerate(keys):
        st = t0 + max(0.0, starts[j] - 0.05); en = t0 + (starts[j + 1] - 0.05 if j + 1 < len(keys) else dur)
        timing.append({"key": k, "text": TEXT[k], "start": round(st, 3), "end": round(en, 3)})
    WORDS.extend([[w, round(t0 + t, 3)] for w, t in RAW[-1] if w])
    chunks += [x, np.zeros(int(gap * SR), dtype=np.float32)]; t0 += dur + gap

audio = np.concatenate(chunks); audio = audio / (np.max(np.abs(audio)) or 1) * 0.89
total = round(len(audio) / SR, 3)
sf.write(f"{PROJ}/assets/voice.wav", audio, SR)
T = {l["key"]: l["start"] for l in timing}; T["end"] = total; E = {l["key"]: l["end"] for l in timing}
json.dump({"model": MODEL, "voice": VOICE, "tempo": TEMPO, "total": total, "lines": timing, "words": WORDS}, open(f"{PROJ}/assets/timing.json", "w"), indent=1)
with open(f"{PROJ}/assets/timing.js", "w") as f:
    f.write("window.__T = " + json.dumps(T) + ";\nwindow.__E = " + json.dumps(E) + ";\n")
    f.write("window.__W = " + json.dumps(WORDS) + ";\n")
    f.write("window.__LINES = " + json.dumps([[l["start"], l["text"], l["end"], l["key"]] for l in timing]) + ";\n")
print(f"total {total:.2f}s  ({MODEL}, {VOICE}, tempo {TEMPO}, {len(PARAS)} paragraphs)")
for l in timing: print(f"{l['start']:6.2f} {l['end']:6.2f}  {l['key']:7s} {l['text']}")
