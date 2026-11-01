"""Generate a music track on Venice. usage: python3 music.py <model> <seconds> <out.mp3> "<prompt>" """
import json, sys, time, base64, urllib.request
from venice import _key
model, secs, out, prompt = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
def post(path, body):
    r = urllib.request.Request("https://api.venice.ai/api/v1" + path, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json"})
    resp = urllib.request.urlopen(r, timeout=300); ct = resp.headers.get("Content-Type", ""); data = resp.read()
    return ct, data
spec = [m for m in json.load(urllib.request.urlopen(urllib.request.Request("https://api.venice.ai/api/v1/models?type=music", headers={"Authorization": "Bearer " + _key()})))["data"] if m["id"] == model][0]["model_spec"]
body = {"model": model, "prompt": prompt}
if spec.get("supports_force_instrumental") or spec.get("constraints", {}).get("supports_force_instrumental"): body["force_instrumental"] = True
if "durations" in json.dumps(spec.get("pricing", {})) or spec.get("min_duration"): body["duration_seconds"] = secs
ct, d = post("/audio/queue", body); q = json.loads(d); print("queued", {k: v for k, v in q.items() if k != "audio"})
qid = q.get("queue_id") or q.get("id")
for i in range(120):
    time.sleep(5)
    ct, d = post("/audio/retrieve", {"model": model, "queue_id": qid})
    if "json" in ct:
        j = json.loads(d)
        if j.get("status") in ("PROCESSING", "QUEUED", "processing", "queued"): continue
        a = j.get("audio") or j.get("data") or j.get("audio_base64")
        if isinstance(a, str): open(out, "wb").write(base64.b64decode(a.split(",")[-1])); print("saved", out); break
        print("unexpected", str(j)[:300]); break
    else: open(out, "wb").write(d); print("saved", out, ct); break
