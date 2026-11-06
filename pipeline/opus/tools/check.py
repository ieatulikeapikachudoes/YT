"""Free code checks for Nothing Personal shorts. No models, no API calls.

usage:
  python3 check.py board <short_dir> <V>      storyboard check on proj-<V>/index.html (before render):
                                              one still per line -> empty / tiny-subject frames, plus a 4 fps motion scan
  python3 check.py voice <short_dir> <V>      pronunciation check (recognizer vs script) + story/lesson split (gospel line at 60%+ of runtime)
  python3 check.py final <mp4> [cover.jpg]    final check on the rendered video: motion scan, black or frozen frames,
                                              audio level, clipping, long silences, length; writes a contact sheet
                                              (+ cover) for the judge agent to look at

Every check prints PASS or a list of FLAGS with timestamps. Exit code 1 if anything is flagged.
Calibrated on Law 31: the slow camera push scores ~10 on the motion meter, real animation 20+.
"""
import glob, json, os, re, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MOTION_EVENT = 20      # % of pixels changed in the busiest 80x80 block (full-res) between frames 0.25 s apart
STATIC_MAX = 3.0       # seconds with no motion event before we flag
CAP_Y = (1360, 1600)   # caption band, ignored by the motion scan


def load_small(p):
    return np.asarray(Image.open(p).convert("L").resize((270, 480))).astype(float)


def motion_scan(frames, fps):
    """frames: list of paths at a fixed fps. Returns (events, flags)."""
    A = [load_small(f) for f in frames]
    zone = lambda a: np.vstack([a[60:CAP_Y[0] // 4], a[CAP_Y[1] // 4:400]])      # subject zone minus captions
    ev = []
    for i in range(1, len(A)):
        d = np.abs(zone(A[i]) - zone(A[i - 1])) > 25
        h, w = d.shape; bs = 20
        v = d[:h // bs * bs, :w // bs * bs].reshape(h // bs, bs, w // bs, bs).mean(axis=(1, 3)).max() * 100
        if v >= MOTION_EVENT: ev.append(i / fps)
    end = len(A) / fps
    gaps = [(a, b) for a, b in zip([0.0] + ev, ev + [end]) if b - a > STATIC_MAX]
    return ev, [f"STATIC {a:.1f}s to {b:.1f}s: nothing moves for {b - a:.1f}s. Add a beat (pop, swap, move) in that stretch." for a, b in gaps]


def frame_issues(paths, labels, line_art=False):
    """Near-empty frames and tiny subjects, one still per line (logic from the old factory's code check)."""
    out = []
    for p, lab in zip(paths, labels):
        a = np.asarray(Image.open(p).convert("RGB").resize((270, 480))).astype(int)
        zone = a[60:340, 20:250]
        bg = np.median(zone.reshape(-1, 3), axis=0)
        mask = np.abs(zone - bg).sum(axis=2) > 60
        cover = mask.mean(); rows = np.where(mask.mean(axis=1) > 0.04)[0]
        height = (rows[-1] - rows[0]) / 480 if len(rows) else 0
        if cover < (0.012 if line_art else 0.05): out.append(f"EMPTY {lab}: only {cover:.0%} of the subject zone has content. Add a big central subject.")
        elif height < 0.30: out.append(f"SMALL {lab}: main subject is {height:.0%} of frame height. Scale it to 35 to 50%.")
    return out


def snap(index_html, outdir, times):
    shutil.rmtree(outdir, ignore_errors=True)
    r = subprocess.run(["node", os.path.join(HERE, "snap.mjs"), os.path.abspath(index_html), outdir, ",".join(f"{t:.2f}" for t in times)],
                       capture_output=True, text=True, timeout=1800)
    errs = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else ["snap failed: " + r.stderr[-300:]]
    return sorted(glob.glob(f"{outdir}/*.jpg")), errs


def board(short_dir, V):
    P = f"{short_dir}/proj-{V}"; tm = json.load(open(f"{P}/assets/timing.json")); L = tm["lines"]
    flags = []
    stills = [round(l["start"] + 0.75 * (l["end"] - l["start"]), 2) if i else round(min(1.0, l["end"] - 0.2), 2) for i, l in enumerate(L)]
    paths, errs = snap(f"{P}/index.html", f"{short_dir}/check-{V}/stills", stills)
    flags += [f"JS ERROR: {e}" for e in errs if "WT miss" not in e] + [f"TIMING: {e} (a beat fell back to the line start)" for e in errs if "WT miss" in e]
    style = json.load(open(f"{short_dir}/short.json")).get("style", "flat")
    flags += frame_issues(paths, [f"line {l['key']} ({t:.1f}s)" for l, t in zip(L, stills)], style in ("ink", "paper"))
    ts = [i / 4 for i in range(int(tm["total"] * 4))]
    mpaths, _ = snap(f"{P}/index.html", f"{short_dir}/check-{V}/motion", ts)
    flags += motion_scan(mpaths, 4)[1]
    sheet(paths, [f"{l['key']} {t:.1f}s" for l, t in zip(L, stills)], f"{short_dir}/check-{V}/board.jpg")
    report(f"board {V}", flags, f"{short_dir}/check-{V}/board.jpg")


def sheet(paths, labels, out, cover=None, cols=8, w=200):
    h = int(w * 16 / 9); n = len(paths) + (1 if cover else 0); rows = (n + cols - 1) // cols
    im = Image.new("RGB", (cols * w, rows * (h + 26)), "#111")
    d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception: f = ImageFont.load_default()
    items = list(zip(paths, labels)) + ([(cover, "COVER")] if cover else [])
    for i, (p, lab) in enumerate(items):
        x, y = (i % cols) * w, (i // cols) * (h + 26)
        im.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y + 26)); d.text((x + 6, y + 4), lab, fill="#ffd23f" if lab == "COVER" else "#fff", font=f)
    im.save(out, quality=85)


def final(mp4, cover=None):
    work = os.path.splitext(mp4)[0] + "-check"; shutil.rmtree(work, ignore_errors=True); os.makedirs(f"{work}/m"); os.makedirs(f"{work}/s")
    flags = []
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout)
    if not 30 <= dur <= 62: flags.append(f"LENGTH {dur:.1f}s is outside 30 to 62s.")
    subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "fps=4,scale=270:480", f"{work}/m/f%04d.png"], check=True)
    mf = sorted(glob.glob(f"{work}/m/*.png"))
    flags += motion_scan(mf, 4)[1]
    dark = [i / 4 for i, p in enumerate(mf) if load_small(p).mean() < 8]
    if dark: flags.append(f"BLACK frames at {', '.join(f'{t:.2f}s' for t in dark[:6])}{' ...' if len(dark) > 6 else ''}")
    if load_small(mf[-1]).std() < 6: flags.append("LAST FRAME is nearly blank. End on a clear image.")
    a = subprocess.run(["ffmpeg", "-nostats", "-i", mp4, "-af", "volumedetect,silencedetect=n=-45dB:d=1.2", "-f", "null", "-"], capture_output=True, text=True).stderr
    mean = float(re.search(r"mean_volume: ([-\d.]+)", a).group(1)); peak = float(re.search(r"max_volume: ([-\d.]+)", a).group(1))
    if mean < -28: flags.append(f"AUDIO quiet: mean {mean:.1f} dB (aim for -24 to -16).")
    if mean > -12: flags.append(f"AUDIO loud: mean {mean:.1f} dB.")
    if peak >= -0.1: flags.append(f"AUDIO clipping: peak {peak:.1f} dB.")
    for s, e in re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", a):
        flags.append(f"SILENCE {float(s):.1f}s to {float(e):.1f}s.")
    subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "fps=1", f"{work}/s/s%03d.jpg"], check=True)
    sp = sorted(glob.glob(f"{work}/s/*.jpg"))
    sheet(sp, [f"{i}s" for i in range(len(sp))], f"{work}/sheet.jpg", cover)
    report(f"final {os.path.basename(mp4)} ({dur:.1f}s, audio mean {mean:.1f} dB, peak {peak:.1f} dB)", flags, f"{work}/sheet.jpg")


NUMS = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
def norm(w): w = re.sub(r"[^a-z0-9]", "", w.lower()); return NUMS.get(w, w)

def voice(short_dir, V):
    import difflib
    sc = json.load(open(f"{short_dir}/script-{V}.json")); tm = json.load(open(f"{short_dir}/proj-{V}/assets/timing.json"))
    said = [norm(w) for l in sc["lines"] for w in re.sub(r"\[[^\]]*\]", " ", l.get("say") or l["text"]).replace("-", " ").split() if norm(w)]
    heard = [(norm(w), t) for w, t in tm["words"] if norm(w)]
    sm = difflib.SequenceMatcher(a=said, b=[h for h, _ in heard], autojunk=False); flags = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal": continue
        exp = " ".join(said[a0:a1]); got = " ".join(h for h, _ in heard[b0:b1]); t = heard[b0][1] if b0 < len(heard) else tm["total"]
        if re.sub(r"\s", "", exp) == re.sub(r"\s", "", got): continue
        if exp.rstrip("s") == got.rstrip("s"): continue                       # plural s swallowed by the next word (friends sent / friend sent)          # same letters, split differently (court side / courtside)
        if exp.isdigit() or got.isdigit() or re.fullmatch(r"[0-9a-z]{1,3}", got or "x"): continue   # numbers and short tokens (5am / a m) are noisy
        flags.append(f"VOICE at {t:.1f}s: script says '{exp}', recognizer heard '{got}'. Listen, and if it is wrong spell it out in the line's \"say\" field.")
    g = [l for l in tm["lines"] if re.sub(r"[^a-z ]", "", l["text"].lower()).startswith("here is the gospel")]
    if g:
        share = g[0]["start"] / tm["total"]; lesson = tm["total"] - g[0]["start"]
        if share < 0.6: flags.append(f"LESSON EARLY: 'Here is the gospel' starts at {g[0]['start']:.1f}s, {share:.0%} of {tm['total']:.1f}s. The story should be about two-thirds: start it at 60% or later (add story or cut lesson).")
        if lesson > 22: flags.append(f"LESSON LONG: the lesson runs {lesson:.1f}s. Keep it to about 18 s (one proof max).")
        print(f"story {g[0]['start']:.1f}s ({share:.0%}), lesson {lesson:.1f}s")
    print(f"voice match {sm.ratio():.0%}"); report(f"voice {V}", flags, "(no sheet)")


def report(name, flags, sheet_path):
    print(f"== {name}")
    print("PASS" if not flags else "\n".join(f"- {x}" for x in flags))
    if not sheet_path.startswith("("): print(f"contact sheet: {sheet_path}")
    if flags: sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    if sys.argv[1] == "board": board(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "voice": voice(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "final": final(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else: sys.exit(__doc__)
