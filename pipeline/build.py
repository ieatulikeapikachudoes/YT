"""Fill the scene timings into a short's template and write the HyperFrames index.html.

usage: python3 pipeline/build.py shorts/01-friend

Reads  <short>/template.html            placeholders: __TOTAL__, __SA_DUR__, __SB_START__/__SB_DUR__ ... __GUY_START__/__GUY_DUR__
       <short>/project/assets/timing.json
       <short>/scenes.json (optional)    {"sA": ["0", "prof"], "sB": ["prof", "think"], ...}  scene bounds as line keys; "0" and "end" allowed
Writes <short>/project/index.html
"""
import json, os, sys

short = os.path.abspath(sys.argv[1])
tm = json.load(open(f"{short}/project/assets/timing.json"))
T = {l["key"]: l["start"] for l in tm["lines"]}
T["0"] = 0.0
T["end"] = tm["total"]
total = tm["total"]

default_scenes = {
    "sA": ["0", "prof"],
    "sB": ["prof", "think"],
    "sC": ["think", "grad"],
    "sD": ["grad", "fix"],
    "sE": ["fix", "end"],
}
scenes = json.load(open(f"{short}/scenes.json")) if os.path.exists(f"{short}/scenes.json") else default_scenes

def r(x): return f"{x:.3f}"

s = open(f"{short}/template.html").read()
s = s.replace("__TOTAL__", r(total))
for k, (a, b) in scenes.items():
    a, b = T[a], T[b]
    s = s.replace(f"__{k.upper()}_START__", r(a)).replace(f"__{k.upper()}_DUR__", r(b - a))
    s = s.replace(f"__{k.upper()}_END__", r(b))
guy_start = T.get("hear", 0.0) - 0.3
s = s.replace("__GUY_START__", r(max(0.0, guy_start))).replace("__GUY_DUR__", r(total - max(0.0, guy_start)))
open(f"{short}/project/index.html", "w").write(s)
print("built", f"{short}/project/index.html", "total", total)
