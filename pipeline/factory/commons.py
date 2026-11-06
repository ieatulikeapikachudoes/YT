"""Wikimedia Commons stock finder for Nothing Personal.

Searches Commons for photos or clips of a specific place, object or event, keeps ONLY files that are
public domain, CC0 or CC BY (no BY-SA, no NC, no ND, no "fair use"), downloads them, and writes the credit
line for each one so it can go in the video description.

usage:
  python3 commons.py search "Oder river Frankfurt" [--video] [--n 8]      # list matches with license + credit
  python3 commons.py get "File:Oder river.jpg" out_dir [--width 1600]   # download one file + append credits.json

Needs network access to commons.wikimedia.org and upload.wikimedia.org.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "NothingPersonal-pipeline/1.0 (faceless explainer shorts; contact via YouTube channel)"}
OK = re.compile(r"^(public domain|pd\b|pd-|cc0|cc[- ]?by[- ]?\d|cc[- ]?by$)", re.I)
BAD = re.compile(r"sa|nc|nd|fair use|non-free", re.I)


def _open(url, timeout=60):
    """urlopen that waits and retries when Wikimedia rate-limits (429), as their API rules ask."""
    for i in range(6):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 5: raise
            wait = int(e.headers.get("retry-after") or 10) + 2
            if wait > 90: sys.exit(f"Wikimedia rate limit: told to wait {wait}s. Try again later or run from the Mac.")
            print(f"  rate limited, waiting {wait}s", file=sys.stderr); time.sleep(wait)


def _get(params):
    q = urllib.parse.urlencode({**params, "format": "json", "formatversion": 2, "maxlag": 5})
    return json.load(_open(f"{API}?{q}", 30))


def _clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def license_ok(lic):
    lic = (lic or "").strip()
    if not lic: return False
    if lic.lower().startswith(("public domain", "pd", "cc0")): return True
    return bool(OK.match(lic)) and not BAD.search(lic.lower().replace("cc by", "").replace("cc-by", ""))


def info(titles, width=1600):
    d = _get({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
              "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width})
    out = []
    for p in d["query"]["pages"]:
        if "imageinfo" not in p: continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        g = lambda k: _clean(m.get(k, {}).get("value", ""))
        lic = g("LicenseShortName")
        out.append({"title": p["title"], "license": lic, "ok": license_ok(lic),
                    "author": g("Artist") or g("Credit") or "Unknown", "license_url": g("LicenseUrl"),
                    "page": ii.get("descriptionurl"), "mime": ii.get("mime"), "w": ii.get("width"), "h": ii.get("height"),
                    "url": ii.get("thumburl") if ii.get("mime", "").startswith("image/") else ii.get("url"),
                    "original": ii.get("url"), "desc": g("ImageDescription")[:160]})
    return out


def credit(f):
    name = f["title"].removeprefix("File:")
    return f'"{name}" by {f["author"]}, {f["license"]}, via Wikimedia Commons ({f["page"]})'


def search(q, video=False, n=8):
    ft = "filetype:video" if video else "filetype:bitmap"
    d = _get({"action": "query", "list": "search", "srsearch": f"{q} {ft}", "srnamespace": 6, "srlimit": n * 3})
    titles = [h["title"] for h in d["query"]["search"]]
    res = [f for f in info(titles) if f["ok"]] if titles else []
    return res[:n]


def get(title, out_dir, width=1600):
    f = info([title], width)
    if not f: sys.exit(f"not found: {title}")
    f = f[0]
    if not f["ok"]: sys.exit(f"REFUSED: {title} is '{f['license']}', only public domain / CC0 / CC BY allowed")
    os.makedirs(out_dir, exist_ok=True)
    # originals come from upload.wikimedia.org; resized copies redirect to thumb.wikimedia.org, so shrink locally
    ext = os.path.splitext(urllib.parse.urlparse(f["original"]).path)[1].lower() or ".jpg"
    path = os.path.join(out_dir, re.sub(r"[^A-Za-z0-9._-]+", "_", f["title"].removeprefix("File:"))[:80])
    path = os.path.splitext(path)[0] + ext
    with _open(f["original"], 300) as r, open(path, "wb") as o:
        o.write(r.read())
    if f["mime"] in ("image/jpeg", "image/png", "image/webp", "image/tiff"):
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        os.remove(path); path = os.path.splitext(path)[0] + ".jpg"; im.save(path, quality=90)
    elif f["mime"].startswith("video/"):
        import subprocess
        mp4 = os.path.splitext(path)[0] + ".mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf", f"scale='min({width},iw)':-2", "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an", mp4], check=True)
        os.remove(path); path = mp4
    cj = os.path.join(out_dir, "credits.json")
    cr = json.load(open(cj)) if os.path.exists(cj) else []
    cr = [c for c in cr if c["title"] != f["title"]] + [{**f, "file": os.path.basename(path), "credit": credit(f)}]
    json.dump(cr, open(cj, "w"), indent=1)
    print("saved", path); print("credit:", credit(f))
    return path


def credits_block(out_dir):
    """Text to paste at the end of the YouTube/TikTok description."""
    cj = os.path.join(out_dir, "credits.json")
    if not os.path.exists(cj): return ""
    return "Images: " + "; ".join(c["credit"] for c in json.load(open(cj)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    flag = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if a[0] == "search":
        for f in search(a[1], "--video" in a, int(flag("--n", 8))):
            print(f'{f["title"]}\n   {f["license"]} | {f["w"]}x{f["h"]} | {f["author"][:60]}\n   {f["desc"]}')
    elif a[0] == "get":
        get(a[1], a[2], int(flag("--width", 1600)))
    elif a[0] == "credits":
        print(credits_block(a[1]))
