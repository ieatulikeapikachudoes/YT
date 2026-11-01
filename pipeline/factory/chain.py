"""Steps 1-3: topics -> research -> script -> 2 blind judge loops (all change requests auto-applied)."""
import json, os, re, sys, venice
R = json.load(open("routing.json")); M = lambda s: R[s]["model"]
CH = open("channel.md").read()
def W(p, s): os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(s if isinstance(s, str) else json.dumps(s, indent=1))
def clean(s): return s.replace("—", ",").replace("–", ",").replace(" ,", ",")

def topics(n=5):
    done = sorted(os.listdir("runs")) if os.path.isdir("runs") else []
    p = f"""{CH}

You are the orchestrator for the next batch. Propose {n} short video briefs for this channel.
They MUST differ from each other: different topic lanes, at least 3 different visual styles, at least 3 different voices, and a mix of formats
(e.g. one thought experiment, one dark history or power story, one relationship or social pain, one money or status mechanism, one AI or future piece).
Avoid repeating past shorts. Already made in this factory: {done}.
Each brief needs a pain a stranger feels, a sharp angle and a mechanism reveal.

Return JSON only: [{{"slug": "kebab-case-3-words", "topic": "...", "lane": "...", "pain": "...", "angle": "...", "reveal": "the mechanism the payoff explains",
"style": "flat|mono|ink|paper", "voice": "<kokoro voice id>", "needs_research": true|false, "research_questions": ["..."]}}]"""
    return venice.jsonish(venice.chat(M("topics"), p, max_tokens=4000, temperature=0.9, tag="topics"))

def research(b, d):
    p = f"""Research for a 60 second explainer short. Topic: {b['topic']}. Angle: {b['angle']}.
Answer these with checkable facts, numbers and dates: {b.get('research_questions')}
Rules: only facts you can source. Give each fact with its source name and URL. Flag anything contested. Plain bullet list, under 400 words."""
    r = venice.chat(M("research"), p, web=True, max_tokens=3000, temperature=0.2, tag=f"research:{b['slug']}")
    W(f"{d}/research.md", r); return r

SCRIPT_FMT = """Return JSON only:
{"title": "...", "lines": [{"key": "h1", "sec": "hook|loop|body|payoff|end", "text": "caption text", "say": "same text spelled for TTS if any word is hard to pronounce, else omit"}]}
Keys: short lowercase ids (h1, h2, loop, b1, b2..., p1, p2, fin). Never use the key "end". One sentence or two short ones per line. 10 to 18 lines.
Write numbers in "text" as digits and in "say" as words."""

def write_script(b, d, research_txt):
    p = f"""{CH}

Write the script for this brief:
{json.dumps(b, indent=1)}

Research (use only what is backed here; do not invent numbers):
{research_txt or "none needed, this is a thesis or thought experiment piece"}

{SCRIPT_FMT}"""
    s = venice.jsonish(venice.chat(M("script"), p, max_tokens=3000, temperature=0.8, tag=f"script:{b['slug']}"))
    for l in s["lines"]: l["text"] = clean(l["text"]); l.setdefault("say", None)
    return s

JUDGE = """You are a judge. You did not write this script and have no stake in it. Find what is weak, say it plainly, propose fixes.
Check: Hook (claim first, would a stranger stop by second 3?). Open loop (does the payoff answer that exact question?). Reveal (a mechanism, not a guessable fact).
Claims (anything a smart commenter will catch; absolute words not backed). Logic jumps. Voice (deadpan, no hedging, no filler, no essay sentences).
Drawable (every line has a concrete thing to show). Cut lines that lose nothing. Quotable line. Likely top comment objection. Ending (one cold line, loops to hook?).
Hard rules: no em dashes, channel name never appears, 120 to 190 words.

Output plain text:
VERDICT: Ship / Fix then ship / Rewrite, one sentence.
CHANGE REQUESTS: numbered, one line each, each with the exact replacement wording where it is a text change."""

def judge(b, s, research_txt, tag):
    lines = "\n".join(f"{i+1} {l['key']} [{l['sec']}] {l['text']}" for i, l in enumerate(s["lines"]))
    p = f"""{JUDGE}

Channel context:
{CH}

Research backing (if any):
{research_txt or 'none'}

Script "{s['title']}":
{lines}"""
    return venice.chat(M("script_judge"), p, max_tokens=3000, temperature=0.3, tag=tag)

def revise(b, s, notes, tag):
    p = f"""{CH}

Apply EVERY change request below to this script. Do not add anything else. Keep the structure and line keys where possible.

Script:
{json.dumps(s, indent=1)}

Change requests:
{notes}

{SCRIPT_FMT}"""
    s2 = venice.jsonish(venice.chat(M("script"), p, max_tokens=3000, temperature=0.4, tag=tag))
    for l in s2["lines"]: l["text"] = clean(l["text"]); l.setdefault("say", None)
    return s2

def run(b):
    d = f"runs/{b['slug']}"; W(f"{d}/brief.json", b)
    rt = research(b, d) if b.get("needs_research") else ""
    s = write_script(b, d, rt); W(f"{d}/script_v0.json", s)
    for r in (1, 2):
        n = judge(b, s, rt, f"sjudge{r}:{b['slug']}"); W(f"{d}/script_judge_{r}.md", n)
        s = revise(b, s, n, f"revise{r}:{b['slug']}"); W(f"{d}/script_v{r}.json", s)
    s["voice"] = b["voice"]; s["style"] = b["style"]
    for i, l in enumerate(s["lines"]):
        if l["key"] in ("end", "") : l["key"] = f"x{i}"
    keys = [l["key"] for l in s["lines"]]
    if len(set(keys)) != len(keys):
        for i, l in enumerate(s["lines"]): l["key"] = f"{l['key']}{i}"
    W(f"{d}/script.json", s)
    wc = sum(len(l["text"].split()) for l in s["lines"])
    print(f"[{b['slug']}] {s['title']} | {len(s['lines'])} lines | {wc} words")

if __name__ == "__main__":
    if sys.argv[1] == "topics":
        t = topics(); W("runs/_batch.json", t)
        for x in t: print(f"- {x['slug']} | {x['style']} | {x['voice']} | {x['topic']} || {x['angle']}")
    elif sys.argv[1] == "run":
        for b in json.load(open("runs/_batch.json")):
            if sys.argv[2:] and b["slug"] not in sys.argv[2:]: continue
            run(b)
