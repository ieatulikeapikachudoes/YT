"""build.py <short_dir> <version>: kit + scenes.js + beats.js + timing -> <short_dir>/proj-<V>/index.html
Run voice.py first (it writes proj-<V>/assets/timing.json). Captions are 1 to 3 word chunks, keywords from short.json in gold."""
import json, re, shutil, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.join(HERE, "..", "kit")
D, V = sys.argv[1], sys.argv[2]; P = f"{D}/proj-{V}"; cfg = json.load(open(f"{D}/short.json"))
for f in ["fonts", "vendor"]: shutil.copytree(f"{KIT}/{f}", f"{P}/{f}", dirs_exist_ok=True)
for f in ["hyperframes.json", "package.json"]: shutil.copy(f"{KIT}/{f}", P)
tm = json.load(open(f"{P}/assets/timing.json")); W = tm["words"]; KEY = set(cfg.get("keywords", []))
caps = []
for li, l in enumerate(tm["lines"]):
    toks = l["text"].split(); last = li == len(tm["lines"]) - 1
    ws = [w for w in W if l["start"] - 0.01 <= w[1] < l["end"] + (0.5 if last else 0)]
    times = [w[1] for w in ws] if len(ws) == len(toks) else [l["start"] + (l["end"] - l["start"]) * i / len(toks) for i in range(len(toks))]
    i = 0
    while i < len(toks):
        g = [i]
        while len(g) < 3 and g[-1] + 1 < len(toks) and not re.search(r"[.,?!\"]$", toks[g[-1]]) and sum(len(toks[j]) for j in g) + len(toks[g[-1] + 1]) <= 13: g.append(g[-1] + 1)
        out = []
        for j in g:
            t = re.sub(r"[.,]+$", "", toks[j]).replace('"', ""); bare = t.lower().strip("?!")
            out.append(f"<b>{t}</b>" if bare in KEY else t)
        caps.append({"html": " ".join(out), "t0": round(times[g[0]] - 0.04, 3)}); i = g[-1] + 1
for k, c in enumerate(caps): c["t1"] = round(caps[k + 1]["t0"] - 0.01, 3) if k + 1 < len(caps) else tm["total"]
h = open(f"{KIT}/kit.html").read()
h = h.replace("/*SCENES*/", open(f"{D}/scenes.js").read()).replace("/*BEATS*/", open(f"{D}/beats.js").read())
h = h.replace("__VERSION__", V).replace("__LAW__", str(cfg.get("law") or "")).replace("__CAPS__", json.dumps(caps)).replace("__TOTAL__", f"{tm['total']:.3f}")
if not os.path.exists(f"{P}/assets/mix.wav"): shutil.copy(f"{P}/assets/voice.wav", f"{P}/assets/mix.wav")
open(f"{P}/index.html", "w").write(h); print(f"{V}: {len(caps)} caption chunks, {tm['total']:.1f}s -> {P}/index.html")
