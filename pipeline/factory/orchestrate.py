"""Factory v2: one command, DeepSeek orchestrates everything. No Claude calls.
usage: python3 orchestrate.py <batch_name> [n_shorts]
Resumable: every step writes a file; rerunning skips finished steps."""
import json, os, re, subprocess, sys, threading, time, traceback
import numpy as np
from PIL import Image
import venice, chain, storyboard as sb, package

BATCH = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 5
ROOT = f"runs/{BATCH}"; os.makedirs(ROOT, exist_ok=True)
T0 = time.strftime("%H:%M:%S"); LOCK = threading.Lock(); VOICE_LOCK = threading.Lock()
LESSONS = open("lessons.md").read(); RESULTS = open("results.json").read()
chain.CH += "\n\n" + LESSONS                      # every script prompt sees the lessons
sb.RULES += "\n\nLESSONS FROM PAST BATCHES:\n" + LESSONS
package.OUT = f"/home/claude/np/out/{BATCH}"
BRAIN = "deepseek-v4-pro"
_chat = venice.chat
def _tagged(*a, **k):
    k["tag"] = BATCH + ":" + k.get("tag", "") if not k.get("tag", "").startswith(BATCH + ":") else k["tag"]
    return _chat(*a, **k)
venice.chat = _tagged
def log(*a):
    with LOCK:
        line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(line, flush=True); open(f"{ROOT}/log.txt", "a").write(line + "\n")
def J(p): return json.load(open(p))
def W(p, o): open(p, "w").write(o if isinstance(o, str) else json.dumps(o, indent=1))
def words(s): return sum(len(l["text"].split()) for l in s["lines"])

# ---------- 1. plan the batch as ONE experiment ----------
def plan():
    p = f"{ROOT}/plan.json"
    if os.path.exists(p): return J(p)
    done = [d for d in os.listdir("runs") if os.path.isdir(f"runs/{d}")]
    prompt = f"""{chain.CH}

Past results on the channel:
{RESULTS}

You are the orchestrator. Design this batch of {N} shorts as ONE experiment that answers ONE question about what grows this channel.
Pick the variable to test (e.g. art style, hook type, narrator voice, topic lane, length) based on the results. Hold everything else as constant as possible
(for example: test style by making the SAME 2 or 3 topics in different styles, or test lanes with the same style and voice).
Lean the topics toward what is already working, unless the question is about lanes. Don't repeat past topics: {done}.

Return JSON only:
{{"question": "...", "variable": "...", "held_constant": "...", "why": "one sentence from the results",
 "briefs": [{{"slug": "kebab-case-3-words-unique", "topic": "...", "lane": "...", "pain": "...", "angle": "...", "reveal": "...",
 "style": "flat|mono|ink|paper", "voice": "bm_george|am_michael|af_heart|am_onyx|bf_emma", "variant": "what this short tests", "needs_research": true|false, "research_questions": ["..."]}}]}}"""
    pl = venice.jsonish(venice.chat(BRAIN, prompt, max_tokens=5000, temperature=0.8, tag=f"{BATCH}:plan"))
    slugs = set()
    for b in pl["briefs"]:
        while b["slug"] in slugs: b["slug"] += "-b"
        slugs.add(b["slug"])
    W(p, pl); log("PLAN:", pl["question"], "| variable:", pl["variable"]); return pl

# ---------- 2. script: write, 2 judges, fact check, length gate ----------
FACT = """You are a fact checker. List every factual claim in this script (numbers, dates, studies, named people, 'researchers found').
For each: is it backed by the research below? If not backed, write a change request that cuts it or makes it qualitative without a number.
Output plain text. If everything is backed or there are no factual claims, output exactly: NONE"""
def script_step(b, d):
    if os.path.exists(f"{d}/script.json"): return J(f"{d}/script.json")
    rt = open(f"{d}/research.md").read() if os.path.exists(f"{d}/research.md") else (chain.research(b, d) if b.get("needs_research") else "")
    s = chain.write_script(b, d, rt); W(f"{d}/script_v0.json", s)
    for r in (1, 2):
        n = chain.judge(b, s, rt, f"{BATCH}:sjudge{r}:{b['slug']}"); W(f"{d}/script_judge_{r}.md", n)
        s = chain.revise(b, s, n, f"{BATCH}:revise{r}:{b['slug']}")
    fc = venice.chat(BRAIN, f"{FACT}\n\nResearch:\n{rt or 'NO RESEARCH WAS DONE: any specific number or study is unbacked.'}\n\nScript:\n" + "\n".join(l["text"] for l in s["lines"]), max_tokens=2000, temperature=0.1, tag=f"{BATCH}:factcheck:{b['slug']}")
    W(f"{d}/factcheck.md", fc)
    if fc.strip().upper() != "NONE": s = chain.revise(b, s, fc, f"{BATCH}:factfix:{b['slug']}")
    for _ in range(2):
        if words(s) <= 165: break
        s = chain.revise(b, s, f"1. The script is {words(s)} words. Cut it to 130-150 words. Keep the hook, loop, payoff and end lines; cut or merge body lines.", f"{BATCH}:trim:{b['slug']}")
    for i, l in enumerate(s["lines"]):
        if l["key"] in ("end", ""): l["key"] = f"x{i}"
    if len({l['key'] for l in s['lines']}) != len(s["lines"]):
        for i, l in enumerate(s["lines"]): l["key"] = f"k{i}"
    s["voice"], s["style"] = b["voice"], b["style"]
    W(f"{d}/script.json", s); log(f"[{b['slug']}] script: {words(s)} words, {len(s['lines'])} lines | fact check: {'clean' if fc.strip().upper() == 'NONE' else 'fixed'}")
    return s

def voice_step(b, d):
    if os.path.exists(f"{d}/proj/assets/timing.json"): return
    os.makedirs(f"{d}/proj", exist_ok=True)
    subprocess.run(f"cp -r kit/fonts kit/vendor kit/hyperframes.json kit/package.json {d}/proj/", shell=True, check=True)
    with VOICE_LOCK:
        sp = "1.08" if b["voice"] == "bm_george" else "1.0"
        r = subprocess.run(["python3", "voice.py", f"{d}/proj", b["voice"], sp, f"{d}/script.json"], capture_output=True, text=True)
    t = [x for x in r.stdout.splitlines() if x.startswith("total")]
    log(f"[{b['slug']}] voice: {t[0] if t else r.stderr[-300:]}")

# ---------- 3. storyboard: draft, 2 vision judges, code check, DeepSeek cleanup ----------
def frame_issues(snapdir, n, line_art=False):
    """Code check: flags near-empty frames and tiny subjects. Free, no model."""
    out = []
    for i in range(n):
        p = f"{snapdir}/frame-{i:02d}.png"
        if not os.path.exists(p): continue
        a = np.asarray(Image.open(p).convert("RGB").resize((270, 480))).astype(int)
        zone = a[60:340, 20:250]                              # subject zone, y 240-1360 at full size
        bg = np.median(zone.reshape(-1, 3), axis=0)
        mask = np.abs(zone - bg).sum(axis=2) > 60
        cover = mask.mean()
        rows = np.where(mask.mean(axis=1) > 0.04)[0]
        height = (rows[-1] - rows[0]) / 480 if len(rows) else 0
        if cover < (0.012 if line_art else 0.05): out.append(f"Frame {i+1}: nearly empty ({cover:.0%} of the subject zone has content). Add a big central subject.")
        elif height < 0.30: out.append(f"Frame {i+1}: main subject too small ({height:.0%} of frame height). Scale it to 35-50% of frame height.")
    return out

def storyboard_step(b, d):
    if os.path.exists(f"{d}/scenes.js"): return
    s = J(f"{d}/script.json"); LA = b["style"] in ("ink", "paper")
    sc, be = sb.code_call(sb.prompt_new(b, s, d), f"{BATCH}:board0:{b['slug']}")
    sc, be, board = sb.fix_errors(d, b, sc, be, "v0")
    _, li = sb.lines_info(d); nlines = len(J(f"{d}/proj/assets/timing.json")["lines"])
    keys = ", ".join(f"{i+1}={l['key']}" for i, l in enumerate(J(f"{d}/proj/assets/timing.json")["lines"]))
    def apply(notes, tag):
        return sb.code_call(f"""Apply EVERY change request below to this storyboard code. Return the full updated two ```js blocks (block 1 scenes, block 2 beats).
Frame numbers count lines in order: {keys}

Change requests:
{notes}

Kit reference:
```js
{sb.KIT}
{sb.MOTION}
```
Palette C = {json.dumps(sb.STYLES[b['style']]['C'])}
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
{sb.RULES}""", tag)
    for r in (1, 2):
        notes = venice.chat(sb.M("board_judge"), f"{sb.JUDGE}\n\nStyle intended: {sb.STYLES[b['style']]['look']}\nScript:\n{li}", images=[board], max_tokens=3000, temperature=0.3, tag=f"{BATCH}:bjudge{r}:{b['slug']}")
        ci = frame_issues(f"{d}/snaps-v{r-1}", nlines, LA)
        if ci: notes += "\n\nMEASURED BY CODE (must fix):\n" + "\n".join(ci)
        W(f"{d}/board_judge_{r}.md", notes)
        sc, be = apply(notes, f"{BATCH}:apply{r}:{b['slug']}")
        sc, be, board = sb.fix_errors(d, b, sc, be, f"v{r}")
    ci = frame_issues(f"{d}/snaps-v2", nlines, LA)                     # the cleanup pass Claude used to do
    if ci:
        W(f"{d}/cleanup.md", "\n".join(ci))
        sc, be = apply("\n".join(ci) + "\nChange nothing else.", f"{BATCH}:cleanup:{b['slug']}")
        sc, be, board = sb.fix_errors(d, b, sc, be, "v3")
    W(f"{d}/scenes.js", sc); W(f"{d}/beats.js", be)
    left = frame_issues(f"{d}/snaps-v3" if ci else f"{d}/snaps-v2", nlines, LA)
    log(f"[{b['slug']}] storyboard done | code check: {len(ci)} issues before cleanup, {len(left)} after")

def one_short(b):
    d = f"{ROOT}/{b['slug']}"; os.makedirs(d, exist_ok=True); W(f"{d}/brief.json", b)
    for step in (script_step, voice_step, storyboard_step):
        for attempt in (1, 2):
            try: step(b, d); break
            except Exception as e:
                log(f"[{b['slug']}] {step.__name__} failed (try {attempt}): {e}")
                open(f"{d}/errors.txt", "a").write(traceback.format_exc())
                if attempt == 2: return False
    return True

def package_step(b):
    d = f"{ROOT}/{b['slug']}"
    if os.path.exists(f"{package.OUT}/{b['slug']}.mp4"): return
    c = package.copy(d); package.cover(d, c, b["style"]); package.render(d)
    log(f"[{b['slug']}] rendered + cover + copy")

def report(pl, ok):
    c = [json.loads(l) for l in open("costs.jsonl")]; c = [x for x in c if x["tag"].startswith(BATCH + ":")]
    usd = sum(x["usd"] for x in c); tin = sum(x["in"] or 0 for x in c); tout = sum(x["out"] or 0 for x in c)
    L = [f"# {BATCH}", f"Question: {pl['question']}", f"Variable: {pl['variable']} | Held constant: {pl['held_constant']}", f"Why: {pl.get('why','')}", "",
         f"Venice: {len(c)} calls, {tin:,} in / {tout:,} out tokens, ${usd:.3f} (${usd/max(1,len(ok)):.3f} per short)", "", "## Shorts"]
    for b in pl["briefs"]:
        d = f"{ROOT}/{b['slug']}"; s = J(f"{d}/script.json") if os.path.exists(f"{d}/script.json") else None
        pk = J(f"{d}/package.json") if os.path.exists(f"{d}/package.json") else {}
        tm = J(f"{d}/proj/assets/timing.json")["total"] if os.path.exists(f"{d}/proj/assets/timing.json") else 0
        L += [f"### {pk.get('yt_title', b['slug'])}", f"- tests: {b.get('variant')} | style {b['style']} | voice {b['voice']} | {tm:.0f}s | {words(s) if s else '?'} words | {'OK' if b['slug'] in ok else 'FAILED'}",
              f"- YouTube: {pk.get('yt_title','')} / {pk.get('yt_desc','').replace(chr(10),' ')}", f"- TikTok: {pk.get('tiktok','')}", ""]
    W(f"{ROOT}/report.md", "\n".join(L)); log(f"REPORT written. Venice ${usd:.3f}")

if __name__ == "__main__":
    pl = plan()
    res = {}
    th = [threading.Thread(target=lambda b=b: res.__setitem__(b["slug"], one_short(b))) for b in pl["briefs"]]
    for t in th: t.start()
    for t in th: t.join()
    ok = [s for s, v in res.items() if v]
    for b in pl["briefs"]:
        if b["slug"] in ok:
            try: package_step(b)
            except Exception as e: log(f"[{b['slug']}] package failed: {e}"); ok.remove(b["slug"])
    report(pl, ok)
    log("DONE", f"{len(ok)}/{len(pl['briefs'])} shorts")
