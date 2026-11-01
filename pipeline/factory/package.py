"""Step 7: copy (titles, captions, cover headline) -> cover image -> render mp4."""
import json, os, re, subprocess, sys, venice
sys.path.insert(0, "kit"); from styles import STYLES
R = json.load(open("routing.json")); M = lambda s: R[s]["model"]
OUT = "/home/claude/np/out/factory"
ENV = dict(os.environ, HYPERFRAMES_BROWSER_PATH="/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell", HYPERFRAMES_SKIP_SKILLS="1")

def copy(d):
    s = json.load(open(f"{d}/script.json"))
    p = f"""Write packaging for this vertical short. Plain words. NEVER use em dashes or en dashes.
Script:
{chr(10).join(l['key'] + ': ' + l['text'] for l in s['lines'])}

Rules:
- cover_headline: clickbait thumbnail text, max 7 words, ALL CAPS, curiosity or pain, not a summary.
- cover_tag: optional 1 to 3 word kicker shown in a pill under the headline, lowercase.
- cover_key: the line key whose frame should sit behind the headline (pick the most striking image, usually the hook).
- yt_title: under 60 characters, keyword first.
- yt_desc: 1 to 2 short lines (keyword in the first line, end with a question), then a new line with #Shorts plus 3 to 4 hashtags.
- tiktok: keyword first, short, one question, then 3 to 5 hashtags.
Return JSON only: {{"cover_headline": "", "cover_tag": "", "cover_key": "", "yt_title": "", "yt_desc": "", "tiktok": ""}}"""
    c = venice.jsonish(venice.chat(M("package"), p, max_tokens=1500, temperature=0.8, tag=f"package:{os.path.basename(d)}"))
    for k, v in c.items(): c[k] = v.replace("—", ",").replace("–", ",") if isinstance(v, str) else v
    json.dump(c, open(f"{d}/package.json", "w"), indent=1); return c

def cover(d, c, style):
    tm = json.load(open(f"{d}/proj/assets/timing.json")); L = {l["key"]: l for l in tm["lines"]}
    l = L.get(c.get("cover_key")) or tm["lines"][0]; t = l["start"] + 0.75 * (l["end"] - l["start"])
    light = style == "paper"; fg, bg = ("#1a1a1a", "#f4efe4") if light else ("#ffffff", "#111111")
    font = '"Patrick", cursive' if style == "ink" else '"Geist", sans-serif'
    h = open(f"{d}/proj/index.html").read()
    add = f'''<style>#captions{{display:none}}#cv{{position:absolute;left:60px;right:60px;top:190px;text-align:center;font-family:{font};font-weight:900;color:{fg};z-index:9}}
#cv .a{{font-size:100px;line-height:1.0;letter-spacing:-0.03em;text-wrap:balance;text-shadow:0 6px 30px {bg}}}#cv .b{{display:inline-block;margin-top:30px;font-size:62px;padding:8px 30px;background:{fg};color:{bg};border-radius:14px}}</style>
<div id="cv"><div class="a">{c["cover_headline"]}</div>{f'<div class="b">{c["cover_tag"]}</div>' if c.get("cover_tag") else ""}</div>
<script>window.__timelines.main.seek({t:.2f});</script></body>'''
    open(f"{d}/proj/cover.html", "w").write(h.replace("</body>", add, 1))
    out = f"{OUT}/{os.path.basename(d)}-cover.jpg"
    subprocess.run(["node", "/home/claude/np/rms/shot.js", os.path.abspath(f"{d}/proj/cover.html"), out], check=True, timeout=120)
    return out

def render(d):
    out = f"{OUT}/{os.path.basename(d)}.mp4"
    subprocess.run(["npx", "hyperframes", "render", os.path.abspath(f"{d}/proj"), "-o", out], env=ENV, check=True, timeout=3000,
                   stdout=open(f"{d}/render.log", "w"), stderr=subprocess.STDOUT, cwd="/home/claude/np")
    return out

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for slug in sys.argv[1:]:
        d = f"runs/{slug}"; b = json.load(open(f"{d}/brief.json"))
        c = copy(d); cv = cover(d, c, b["style"]); mp4 = render(d)
        print(f"[{slug}] {mp4} | {cv} | {c['yt_title']}")
