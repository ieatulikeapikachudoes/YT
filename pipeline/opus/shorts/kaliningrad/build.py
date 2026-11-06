"""Fill template.html with map data, timing and captions -> proj-A/index.html"""
import difflib, json, os, re, shutil
P = "proj-A"; tm = json.load(open(f"{P}/assets/timing.json")); W = tm["words"]
KEY = set(json.load(open("short.json"))["keywords"])
n = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
caps = []
for li, l in enumerate(tm["lines"]):
    toks = l["text"].replace("south-east", "south-east").split()
    ws = [w for w in W if l["start"] - 0.05 <= w[1] < l["end"] + (0.5 if li == len(tm["lines"]) - 1 else 0)]
    # align script words to heard words; unmatched words get interpolated times
    sm = difflib.SequenceMatcher(a=[n(t) for t in toks], b=[w[0] for w in ws], autojunk=False)
    times = [None] * len(toks)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size): times[a + k] = ws[b + k][1]
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    if not known: known = [(0, l["start"])]
    if known[0][0] != 0: known.insert(0, (0, l["start"]))
    if known[-1][0] != len(toks) - 1: known.append((len(toks) - 1, max(known[-1][1] + 0.25 * (len(toks) - 1 - known[-1][0]), known[-1][1])))
    for (i0, t0), (i1, t1) in zip(known, known[1:]):
        for i in range(i0 + 1, i1): times[i] = t0 + (t1 - t0) * (i - i0) / (i1 - i0)
    for i, t in known: times[i] = t
    i = 0
    while i < len(toks):
        g = [i]
        if i + 1 < len(toks) and not re.search(r"[.,?!]$", toks[i]) and len(toks[i]) + len(toks[i + 1]) <= 13: g.append(i + 1)
        words = []
        for j in g:
            t = re.sub(r"[.,]$", "", toks[j]); bare = n(t.replace("'", ""))
            words.append(f"<b>{t}</b>" if bare in {n(k) for k in KEY} else t)
        caps.append({"html": " ".join(words), "t0": round(times[g[0]] - 0.04, 3)})
        i = g[-1] + 1
for k in range(1, len(caps)): caps[k]["t0"] = max(caps[k]["t0"], caps[k - 1]["t0"] + 0.12)
for k, c in enumerate(caps): c["t1"] = round(caps[k + 1]["t0"] - 0.01, 3) if k + 1 < len(caps) else tm["total"]
h = open("template.html").read().replace("__GEO__", open("geo.json").read()).replace("__RF__", open("relief.json").read()).replace("__CAPS__", json.dumps(caps)).replace("__TOTAL__", f"{tm['total']:.3f}")
os.makedirs(f"{P}/vendor", exist_ok=True); os.makedirs(f"{P}/fonts", exist_ok=True)
shutil.copy("../../kit/vendor/gsap.min.js", f"{P}/vendor/gsap.min.js")
for w in (800, 900): shutil.copy(f"../../node_modules/@fontsource/montserrat/files/montserrat-latin-{w}-normal.woff2", f"{P}/fonts/")
if not os.path.exists(f"{P}/assets/mix.wav"): shutil.copy(f"{P}/assets/voice.wav", f"{P}/assets/mix.wav")
open(f"{P}/index.html", "w").write(h); print(len(caps), "caption chunks")
