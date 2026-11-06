"""shotlist.py <short_dir> [V] [model]: DeepSeek writes the storyboard as a shot list; code builds and checks it.

No animation code from the model. It picks templates from the geo kit (kit/geo/engine.html) and fills their inputs.
Loop: DeepSeek -> schema + timing checks -> geo data -> build -> layout checks -> board motion check.
Any failure goes back to DeepSeek as a list of problems (max 3 schema rounds, 2 layout rounds, 1 motion round).
Needs: <short_dir>/script-V.json, short.json, proj-V/assets/timing.json + voice (run voice.py first).
Writes: shotlist-V.json, proj-V/index.html, shotlist-V.log. Every model call is logged to costs.jsonl (stage "board").
"""
import difflib, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OPUS = os.path.dirname(HERE); KIT = os.path.join(OPUS, "kit", "geo")
sys.path.insert(0, os.path.join(OPUS, ".."))
import venice  # pipeline/venice.py (logs exact tokens to costs.jsonl)

D = os.path.abspath(sys.argv[1]); V = sys.argv[2] if len(sys.argv) > 2 else "A"; MODEL = sys.argv[3] if len(sys.argv) > 3 else "deepseek-v4-flash"
P = f"{D}/proj-{V}"; LOG = open(f"{D}/shotlist-{V}.log", "a")
def log(*a): s = " ".join(str(x) for x in a); print(s); LOG.write(s + "\n"); LOG.flush()
tm = json.load(open(f"{P}/assets/timing.json")); WORDS = tm["words"]; LINES = tm["lines"]; KEYS = [l["key"] for l in LINES]
short = json.load(open(f"{D}/short.json"))
n = lambda w: re.sub(r"[^a-z0-9]", "", str(w).lower())
def heard(i):
    l = LINES[i]; end = LINES[i + 1]["start"] if i + 1 < len(LINES) else tm["total"]
    return [w for w in WORDS if l["start"] - 0.15 <= w[1] < end - 0.05]
HEARD = {l["key"]: heard(i) for i, l in enumerate(LINES)}
def wt(key, word):
    f = n(word)
    for w, t in HEARD[key]:
        if w == f or (len(f) >= 4 and w.startswith(f[:4])): return t
    return None

CATALOG = open(os.path.join(KIT, "catalog.md")).read()
def prompt():
    rows = []
    for i, l in enumerate(LINES):
        end = LINES[i + 1]["start"] if i + 1 < len(LINES) else tm["total"]
        rows.append(f'{l["key"]}  {l["start"]:.1f}s to {end:.1f}s  "{l["text"]}"\n    HEARD: {" ".join(w for w, _ in HEARD[l["key"]])}')
    return CATALOG + "\n\nSCRIPT (one shot per line, in this order):\n" + "\n".join(rows) + "\n\nReturn only the JSON."

def parse(txt):
    t = re.sub(r"^```[a-z]*\s*|\s*```$", "", txt.strip())
    return json.loads(t[t.find("{"): t.rfind("}") + 1])

COLORS = {"red", "ice", "amber", "white", "gray"}
NEED = {"title": ["text"], "card": ["kicker", "lines"], "highlight": ["country"], "label": ["target", "text"], "marker": ["place"], "unit": ["place", "letter"],
        "arrows": ["from", "to"], "line": ["through"], "ring": ["center", "radius_km"], "effect": ["kind"]}
def texts(a): return [a.get("text", ""), a.get("kicker", "")] + list(a.get("lines", []) or [])
def check_schema(sl):
    e = []
    if not isinstance(sl.get("region", {}).get("bbox"), list) or len(sl["region"]["bbox"]) != 4: e.append("region.bbox must be [west, south, east, north]")
    places = sl.get("places", {})
    shots = sl.get("shots", [])
    if [s.get("key") for s in shots] != KEYS: e.append(f"shots must be exactly these keys in order: {KEYS}")
    for i, s in enumerate(shots):
        k = s.get("key")
        if k not in HEARD: continue
        cam = s.get("camera", {})
        if not cam.get("focus"): e.append(f"{k}: camera.focus missing")
        if not 0.8 <= float(cam.get("zoom", 0) or 0) <= 9: e.append(f"{k}: camera.zoom must be 0.8 to 9")
        if s.get("mode", "today") not in ("today", "whatif"): e.append(f"{k}: mode must be today or whatif")
        acts = s.get("actions", [])
        if len(acts) < 2: e.append(f"{k}: needs at least 2 actions (it has {len(acts)})")
        times = []
        labels_alive = 0
        for a in acts:
            d = a.get("do")
            if d not in NEED: e.append(f'{k}: unknown template "{d}"'); continue
            for p in NEED[d]:
                if a.get(p) in (None, "", []): e.append(f"{k}: {d} needs {p}")
            if d == "title" and i != 0: e.append(f"{k}: title is for the hook line only")
            for c in ("color",):
                if a.get(c) and a[c] not in COLORS: e.append(f'{k}: {d}.color "{a[c]}" must be one of {sorted(COLORS)}')
            for t in texts(a):
                if "—" in str(t) or "–" in str(t): e.append(f"{k}: no em or en dashes ({t})")
            if d == "card":
                if len(a.get("kicker", "")) > 34: e.append(f'{k}: card kicker "{a["kicker"]}" is over 34 chars')
                if not 1 <= len(a.get("lines", [])) <= 2: e.append(f"{k}: card needs 1 or 2 lines")
                for t in a.get("lines", []):
                    if len(t) > 18: e.append(f'{k}: card line "{t}" is over 18 chars')
            if d == "label" and len(a.get("text", "")) > 20: e.append(f'{k}: label "{a.get("text")}" is over 20 chars')
            if d == "title" and len(a.get("text", "")) > 26: e.append(f"{k}: title is over 26 chars")
            if d == "unit" and len(str(a.get("letter", ""))) > 3: e.append(f"{k}: unit letter is over 3 chars")
            if d in ("label", "card") and not a.get("until"): labels_alive += 1
            at = a.get("at")
            t = wt(k, at) if at else None
            if t is None: e.append(f'{k}: at "{at}" is not in this line\'s HEARD words; pick one of: {" ".join(w for w, _ in HEARD[k])}')
            else:
                dl = float(a.get("delay", 0) or 0); times.append(t + min(max(dl, 0), 1.5))
                if dl > 1.5: e.append(f'{k}: {d} delay {dl} is over 1.5; anchor it to a later heard word instead')
                lend = LINES[i + 1]["start"] if i + 1 < len(LINES) else tm["total"]
                if not a.get("until") and t + dl > lend - 0.6: e.append(f'{k}: {d} starts after its line is almost over; anchor it to an earlier word')
            u = a.get("until")
            span = (len(KEYS) if u == "end" else KEYS.index(u) + 1 if u in KEYS else i + 1) - i
            if d in ("label", "marker", "unit", "arrows") and span > 2: e.append(f'{k}: {d} "{a.get("text") or a.get("place") or a.get("from")}" stays up for {span} lines; let it go when its line ends (until at most the next line)')
            if u and u != "end" and (u not in KEYS or KEYS.index(u) <= KEYS.index(k)): e.append(f'{k}: until "{u}" must be a LATER line key or "end"')
            for r in [a.get("target"), a.get("place"), a.get("from"), a.get("center")] + list(a.get("to", []) or []) + list(a.get("through", []) or []):
                if r and r not in places and d not in ("label", "highlight") and not (d == "label"): e.append(f'{k}: "{r}" is not in places')
        if labels_alive > 3: e.append(f"{k}: {labels_alive} labels/cards in one line; keep it to 2 or 3")
        start = HEARD[k][0][1] if HEARD[k] else LINES[i]["start"]; end = LINES[i + 1]["start"] if i + 1 < len(LINES) else tm["total"]
        ts = sorted(times)
        if ts and ts[0] > start + 0.8: e.append(f"{k}: first action lands {ts[0] - start:.1f}s into the line; start one on the first heard word")
        for a0, b0 in zip([start] + ts, ts + [end]):
            if b0 - a0 > 3.0: e.append(f"{k}: nothing new happens from {a0:.1f}s to {b0:.1f}s; add an action on a word in that stretch")
    if not isinstance(places, dict) or not places: e.append("places must map every place name to [lon, lat]")
    return e

def geo(sl):
    json.dump(sl, open(f"{D}/shotlist-{V}.json", "w"), indent=1, ensure_ascii=False)
    r = subprocess.run(["node", os.path.join(KIT, "geo_kit.mjs"), f"{D}/shotlist-{V}.json", f"{P}/geo.json"], capture_output=True, text=True, cwd=KIT)
    if r.returncode: return [f"geo step crashed: {r.stderr[-300:]}"]
    return json.load(open(f"{P}/geo.json"))["errors"]

def captions():
    KEY = {n(k) for k in short.get("keywords", [])}; caps = []
    for li, l in enumerate(LINES):
        toks = l["text"].split(); ws = [w for w in WORDS if l["start"] - 0.05 <= w[1] < l["end"] + (0.5 if li == len(LINES) - 1 else 0)]
        sm = difflib.SequenceMatcher(a=[n(t) for t in toks], b=[w[0] for w in ws], autojunk=False); times = [None] * len(toks)
        for a, b, size in sm.get_matching_blocks():
            for q in range(size): times[a + q] = ws[b + q][1]
        known = [(i, t) for i, t in enumerate(times) if t is not None] or [(0, l["start"])]
        if known[0][0] != 0: known.insert(0, (0, l["start"]))
        if known[-1][0] != len(toks) - 1: known.append((len(toks) - 1, known[-1][1] + 0.25 * (len(toks) - 1 - known[-1][0])))
        for (i0, t0), (i1, t1) in zip(known, known[1:]):
            for i in range(i0 + 1, i1): times[i] = t0 + (t1 - t0) * (i - i0) / (i1 - i0)
        for i, t in known: times[i] = t
        i = 0
        while i < len(toks):
            g = [i]
            if i + 1 < len(toks) and not re.search(r"[.,?!]$", toks[i]) and len(toks[i]) + len(toks[i + 1]) <= 13: g.append(i + 1)
            words = [(f"<b>{re.sub(r'[.,]$', '', toks[j])}</b>" if n(toks[j].replace("'", "")) in KEY else re.sub(r"[.,]$", "", toks[j])) for j in g]
            caps.append({"html": " ".join(words), "t0": round(times[g[0]] - 0.04, 3)}); i = g[-1] + 1
    for q in range(1, len(caps)): caps[q]["t0"] = max(caps[q]["t0"], caps[q - 1]["t0"] + 0.12)
    for q, c in enumerate(caps): c["t1"] = round(caps[q + 1]["t0"] - 0.01, 3) if q + 1 < len(caps) else tm["total"]
    return caps

def build(sl):
    os.makedirs(f"{P}/vendor", exist_ok=True); os.makedirs(f"{P}/fonts", exist_ok=True)
    shutil.copy(os.path.join(OPUS, "kit", "vendor", "gsap.min.js"), f"{P}/vendor/")
    for w in (800, 900): shutil.copy(os.path.join(OPUS, f"node_modules/@fontsource/montserrat/files/montserrat-latin-{w}-normal.woff2"), f"{P}/fonts/")
    for f in ("hyperframes.json", "package.json"): shutil.copy(os.path.join(OPUS, "kit", f), P)
    if not os.path.exists(f"{P}/assets/mix.wav"): shutil.copy(f"{P}/assets/voice.wav", f"{P}/assets/mix.wav")
    if not os.path.exists(f"{P}/assets/grain.png"):
        import numpy as np; from PIL import Image
        g = np.random.default_rng(3).integers(0, 255, (1920, 1080), dtype=np.uint8)
        Image.fromarray(np.dstack([g, g, g, np.full((1920, 1080), 110, np.uint8)]), "RGBA").save(f"{P}/assets/grain.png")
    bb = json.dumps(sl["region"]["bbox"])
    stale = not os.path.exists(f"{P}/relief.json") or not os.path.exists(f"{P}/relief.bbox") or open(f"{P}/relief.bbox").read() != bb
    if stale:
        subprocess.run(["node", os.path.join(KIT, "relief_kit.mjs"), f"{P}/geo.json", f"{P}/assets", f"{P}/relief.json"], check=True, cwd=KIT, capture_output=True)
        open(f"{P}/relief.bbox", "w").write(bb)
    h = open(os.path.join(KIT, "engine.html")).read()
    h = h.replace("__SHOTS__", json.dumps(sl, ensure_ascii=False)).replace("__GEO__", open(f"{P}/geo.json").read()).replace("__RF__", open(f"{P}/relief.json").read())
    h = h.replace("__CAPS__", json.dumps(captions(), ensure_ascii=False)).replace("__TOTAL__", f"{tm['total']:.3f}")
    open(f"{P}/index.html", "w").write(h)

def layout():
    r = subprocess.run(["node", os.path.join(KIT, "layout.mjs"), P], capture_output=True, text=True, cwd=KIT)
    try: return [f'{x["key"]}: {x["msg"]}' for x in json.loads(r.stdout.strip().splitlines()[-1])]
    except Exception: return [f"layout check crashed: {r.stderr[-300:]}"]

def board():
    r = subprocess.run(["python3", os.path.join(HERE, "check.py"), "board", D, V], capture_output=True, text=True)
    return [l[2:] for l in r.stdout.splitlines() if l.startswith("- ") and ("STATIC" in l or "JS ERROR" in l)]

SYS = "You are a storyboard artist for short vertical news-map videos. You answer with one JSON object and nothing else."
msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": prompt()}]
def ask(note):
    out = venice.chat(None, model=MODEL, messages=msgs, max_tokens=16000, stage="board", short_dir=D, note=note, temperature=0.4)
    msgs.append({"role": "assistant", "content": out}); return out
def fix(problems, why):
    msgs.append({"role": "user", "content": f"The {why} found these problems. Fix every one, keep everything else the same, and return the whole JSON again:\n- " + "\n- ".join(problems[:25])})

if os.environ.get("REBUILD"):  # rebuild from the saved shot list, no model call
    sl = json.load(open(f"{D}/shotlist-{V}.json")); print("geo:", geo(sl)); build(sl); print("layout:", layout()); print("motion:", board()); sys.exit(0)
rounds = {"schema": 0, "layout": 0, "motion": 0}; sl = None
for attempt in range(8):
    if attempt == 0 and os.environ.get("RESUME"):  # start from the saved shot list instead of a fresh call
        txt = open(f"{D}/shotlist-{V}.json").read(); msgs.append({"role": "assistant", "content": txt})
    else: txt = ask(f"shot list call {attempt + 1}")
    try: sl = parse(txt)
    except Exception as ex: log(f"round {attempt + 1}: not JSON ({ex})"); fix([f"your reply was not valid JSON: {ex}"], "parser"); continue
    errs = check_schema(sl)
    if not errs: errs = geo(sl)
    if errs:
        rounds["schema"] += 1; log(f"round {attempt + 1}: {len(errs)} schema/geo problems"); [log("   ", x) for x in errs[:25]]
        if rounds["schema"] > 3: log("schema rounds used up, stopping"); sys.exit(1)
        fix(errs, "schema checker"); continue
    build(sl); errs = layout()
    if errs and rounds["layout"] < 2:
        rounds["layout"] += 1; log(f"round {attempt + 1}: {len(errs)} layout problems"); [log("   ", x) for x in errs[:25]]
        fix(errs, "layout checker"); continue
    if errs: log(f"layout problems left after 2 rounds: {len(errs)}"); [log("   ", x) for x in errs]
    errs = board()
    if errs and rounds["motion"] < 2:
        rounds["motion"] += 1; log(f"round {attempt + 1}: {len(errs)} motion problems"); [log("   ", x) for x in errs]
        fix(errs, "motion checker"); continue
    if errs: log("motion problems left:", errs)
    log(f"done after {attempt + 1} DeepSeek calls ({rounds})"); break
json.dump(sl, open(f"{D}/shotlist-{V}.json", "w"), indent=1, ensure_ascii=False)
