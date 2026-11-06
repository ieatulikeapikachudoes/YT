"""cover.py <short_dir> <V> "<HEADLINE with <b>gold</b> words>" "<tag>" <seek_seconds> <out.jpg>
Clickbait cover from the short's own frame: captions hidden, headline in black boxes low in the frame, gold tag pill under it."""
import os, subprocess, sys
D, V, HL, TAG, T, OUT = sys.argv[1:7]; P = f"{D}/proj-{V}"
h = open(f"{P}/index.html").read()
add = f'''<style>#caps{{display:none!important}}#cv{{position:absolute;left:50px;right:50px;top:1040px;text-align:center;font-family:"Geist";font-weight:900;z-index:9}}
#cv .a{{display:inline;font-size:104px;line-height:1.14;color:#fff;background:#0b0820;padding:6px 22px;box-decoration-break:clone;-webkit-box-decoration-break:clone;letter-spacing:-0.02em}}
#cv .a b{{color:#ffd23f}}#cv .t{{display:inline-block;margin-top:34px;font-size:54px;padding:10px 30px;background:#ffd23f;color:#3a2200;border-radius:14px;letter-spacing:0.06em;text-transform:uppercase}}</style>
<div id="cv"><span class="a">{HL}</span>{f'<br><span class="t">{TAG}</span>' if TAG else ""}</div>
<script>window.__timelines.main.seek({float(T)});var l=document.getElementById("law");if(l&&LAW)l.style.opacity=1;</script></body>'''
open(f"{P}/cover.html", "w").write(h.replace("</body>", add, 1))
subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "shot.mjs"), os.path.abspath(f"{P}/cover.html"), OUT], check=True)
print("cover ->", OUT)
