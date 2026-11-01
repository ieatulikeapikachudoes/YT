"""Steps 4-5: coder model draws the storyboard from the kit, auto-fixes errors, 2 blind vision-judge loops with changes auto-applied."""
import json, os, re, subprocess, sys, shutil, venice
sys.path.insert(0, "kit"); from styles import STYLES, js as style_js
R = json.load(open("routing.json")); M = lambda s: R[s]["model"]
BASE = open("kit/base.html").read()
KIT = BASE[BASE.index("/* ---------- KIT"):BASE.index("/* ---------- SCENES")]
MOTION = BASE[BASE.index("/* motion helpers"):BASE.index("document.querySelectorAll(\"#dust")]

def lines_info(d):
    tm = json.load(open(f"{d}/proj/assets/timing.json"))
    return tm, "\n".join(f'{l["key"]:6s} {l["start"]:6.2f}-{l["end"]:6.2f}s  "{l["text"]}"' for l in tm["lines"])

EXAMPLE = r"""EXAMPLE of the expected quality and shape (different topic, do not copy it):
```js
const S = {
  h1: [STYLE.bg, F(`${STARS(30)}${GLOW(540, 760, 260, C.a1, 0.2)}${GROUND(1250)}
    ${PERSON(380, 1240, 1.3, { id: "h1-man", face: "sad", pose: "hold", shirt: C.a4 })}
    ${PHONE(700, 880, 1.4, `<circle id="h1-dot" cx="0" cy="-40" r="34" fill="${C.a3}" />${TXT(0, 70, "0 replies", 30, C.fg, 700)}`, "h1-phone")}`)],
  b2: [STYLE.bg, F(`${GLOW(540, 800, 320, C.a3, 0.18)}
    <g id="b2-scale"><path d="M300 900 L780 900" stroke="${C.fg}" stroke-width="14" stroke-linecap="round" /><path d="M540 900 L540 1200" stroke="${C.fg}" stroke-width="14" /></g>
    ${STACK(330, 880, 6, 1.2, "b2-money")}${HEART(760, 860, 1.6, C.a3, "b2-heart")}`)],
};
const SCENE_OF = { h2: "h1" }; const HARD = ["b2"]; const PUSH = { b2: 1.12 };
```
```js
bob("#h1-man .in", 0.2, D("h1"));
tl.fromTo("#h1-dot", { opacity: 1 }, { opacity: 0.2, duration: 0.3, yoyo: true, repeat: 5 }, WT("h1", "waiting"));
pop("#h1-phone .in", WT("h2", "never"));
slideIn("#b2-money .in", T.b2 + 0.1, -200, 0);
tl.to("#b2-scale", { rotation: -8, svgOrigin: "540 900", duration: 0.5, ease: "back.out(2)" }, WT("b2", "heavier"));
pop("#b2-heart .in", WT("b2", "love"));
punch("b2", WT("b2", "love"));
```

"""

RULES = """RULES (follow exactly):
- Output EXACTLY two fenced ```js blocks and nothing else.
  Block 1 defines: const S = { sceneKey: [cssBackground, F(`...svg...`)], ... }; const SCENE_OF = { lineKey: sceneKey }; const HARD = [sceneKeys with hard cuts]; const PUSH = { sceneKey: camScale };
  Block 2 contains only timeline calls (tl.to / tl.fromTo / pop / fadeIn / slideIn / drawOn / bob / shake / punch).
- A scene key is the key of the first line it covers. Every line key either has its own S entry or is mapped by SCENE_OF to an earlier scene. Use 8 to 13 scenes.
- Canvas is 1080x1920. Keep the main subject inside y 260 to 1330 and x 90 to 950. Captions sit at y 1380 to 1560: nothing important there. Keep the bottom 330px and the right 130px free of important things.
- One idea per frame. Main subject big: 35 to 50 percent of frame height. Lots of air. Show the idea of the line as a picture or metaphor, not as text.
- Text inside scenes: only short labels (max 3 words, max 2 per frame). NEVER write the caption sentence on screen.
- Motion: every scene gets at least 2 beats; something new every 2 to 3 seconds. Time beats with WT("lineKey", "word") on the word that matters. The very first scene must be fully visible at t=0 (no fade or pop at time 0 for its main subject).
- Kit objects (G, PERSON, STICK, PHONE, LAPTOP, COIN, STACK, CARD, BUBBLE, HOUSE) have a transform on their outer group. To move, scale or pop them target "#id .in" (their inner group), never the outer id. Only animate x/y/scale on elements WITHOUT a transform attribute, or on "#id .in".
- NEVER use bare tag or class selectors like "path", "text", "circle", ".bar" in beats: they hit every scene. Every selector in block 2 starts with "#".
- Give every element you animate a unique id (prefix ids with the scene key, e.g. "b3-coin"). Don't redefine kit names (C, F, T, E, tl, WT, PERSON...). Use only kit helpers and raw SVG. No images, no external files.
- Use the palette C (fg, ink, panel, muted, ground, skin, a1..a5) and STYLE.bg, or a gradient built from those colors. Template literals must be valid JS."""

def prompt_new(b, s, d):
    st = STYLES[b["style"]]; _, li = lines_info(d)
    return f"""You are a motion designer writing code for an animated vertical short. Style: {b['style']}. Look: {st['look']}
Palette C = {json.dumps(st['C'])}

The kit (already defined, call these):
```js
{KIT}
{MOTION}
```

Script lines (key, start-end seconds, caption text):
{li}

Brief: {b['topic']} | angle: {b['angle']} | reveal: {b['reveal']}

{RULES}

{EXAMPLE}
Make it look crafted: depth (background layer, midground, foreground), glows or shadows where the style allows, a consistent main character across scenes, visual metaphors over literal pictures. Write the two blocks now."""

def split(txt):
    bl = re.findall(r"```(?:js|javascript)?\s*\n(.*?)```", txt, re.S)
    if len(bl) < 2: raise ValueError("expected two js blocks, got %d" % len(bl))
    return bl[0].strip(), bl[1].strip()

def build(d, b, scenes, beats):
    st = STYLES[b["style"]]; tm = json.load(open(f"{d}/proj/assets/timing.json"))
    h = BASE.replace("/*STYLECSS*/", st["cap"]).replace("/*STYLEJS*/", style_js(b["style"])).replace("/*SCENES*/", scenes).replace("/*BEATS*/", beats).replace("__TOTAL__", f"{tm['total']:.3f}")
    open(f"{d}/proj/index.html", "w").write(h)
    open(f"{d}/last_scenes.js", "w").write(scenes); open(f"{d}/last_beats.js", "w").write(beats)

def snap(d, tag):
    tm = json.load(open(f"{d}/proj/assets/timing.json")); L = tm["lines"]
    ts = [round(l["start"] + 0.75 * (l["end"] - l["start"]), 2) if i else round(min(1.0, l["end"] - 0.2), 2) for i, l in enumerate(L)]
    out = f"{d}/snaps-{tag}"; shutil.rmtree(out, ignore_errors=True)
    try:
        rc = subprocess.run(["node", "snap.js", os.path.abspath(f"{d}/proj/index.html"), out, ",".join(map(str, ts))], timeout=200).returncode
    except subprocess.TimeoutExpired: rc = 3
    if rc == 3 or not os.path.exists(f"{out}/errors.json"): return ["page hung during snapshot (likely an infinite loop or a huge repeat count)"], None
    errs = json.load(open(f"{out}/errors.json"))
    board = f"{d}/board-{tag}.jpg"
    subprocess.run(["python3", "../rms/board.py", f"{d}/proj", out, f"{json.load(open(f'{d}/script.json'))['title']} ({tag})", board], check=True)
    return errs, board

def code_call(prompt, tag):
    for attempt in range(2):
        txt = venice.chat(M("storyboard"), prompt, max_tokens=24000, temperature=0.4, tag=tag)
        try: return split(txt)
        except ValueError: continue
    raise RuntimeError("coder failed to return two blocks")

def fix_errors(d, b, sc, be, tag):
    for i in range(3):
        build(d, b, sc, be); errs, board = snap(d, tag)
        if not errs: return sc, be, board
        print(f"  [{tag}] errors: {errs[:3]}")
        sc, be = code_call(f"""This storyboard code throws errors in the browser. Fix them and return the full corrected two ```js blocks (block 1 scenes, block 2 beats). Change nothing else.
Errors: {json.dumps(errs[:8])}

Kit reference:
```js
{KIT}
{MOTION}
```
Block 1:
```js
{sc}
```
Block 2:
```js
{be}
```
{RULES}""", f"fix:{tag}")
    build(d, b, sc, be); errs, board = snap(d, tag)
    return sc, be, board

JUDGE = """You are a storyboard judge for a vertical animated short. You did not make it and have no stake in it. The image is a grid: one frame per spoken line, the caption text is printed under each frame.
Judge each frame as a stranger on a phone for one second, then as an art director:
one idea per frame, subject big enough (35 to 50 percent of height), air around the subject, clean shapes, color discipline (accent only on what matters),
does the picture show the idea of its line (flag decoration, wrong thing, or a literal picture where a sharper metaphor exists, and name the sharper idea),
frame zones (bottom 15 percent and right edge clear for app buttons, nothing important under the caption), text on screen repeating the caption (bad), broken or overlapping elements, empty or near-empty frames, consistency of the main character.
Output plain text:
VERDICT: one sentence.
CHANGE REQUESTS: at most 12, numbered, one line each, naming the frame number and the exact change (what to add, remove, move, resize, recolor, with sizes or positions). Cheapest version that fixes the problem."""

def run(slug):
    d = f"runs/{slug}"; b = json.load(open(f"{d}/brief.json")); s = json.load(open(f"{d}/script.json"))
    sc, be = code_call(prompt_new(b, s, d), f"board0:{slug}")
    sc, be, board = fix_errors(d, b, sc, be, "v0")
    _, li = lines_info(d)
    for r in (1, 2):
        notes = venice.chat(M("board_judge"), f"{JUDGE}\n\nStyle intended: {STYLES[b['style']]['look']}\nScript:\n{li}", images=[board], max_tokens=3000, temperature=0.3, tag=f"bjudge{r}:{slug}")
        open(f"{d}/board_judge_{r}.md", "w").write(notes)
        sc, be = code_call(f"""Apply EVERY change request below to this storyboard code. Return the full updated two ```js blocks (block 1 scenes, block 2 beats).
Frame numbers count lines in order: {', '.join(f'{i+1}={l["key"]}' for i, l in enumerate(json.load(open(f'{d}/proj/assets/timing.json'))['lines']))}

Change requests:
{notes}

Kit reference:
```js
{KIT}
{MOTION}
```
Palette C = {json.dumps(STYLES[b['style']]['C'])}
Script:
{li}

Block 1:
```js
{sc}
```
Block 2:
```js
{be}
```
{RULES}""", f"apply{r}:{slug}")
        sc, be, board = fix_errors(d, b, sc, be, f"v{r}")
    open(f"{d}/scenes.js", "w").write(sc); open(f"{d}/beats.js", "w").write(be)
    print(f"[{slug}] storyboard done -> {board}")

if __name__ == "__main__":
    for s in sys.argv[1:]: run(s)
