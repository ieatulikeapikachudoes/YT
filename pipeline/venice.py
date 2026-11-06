"""Venice AI client for the whole suite: text, images, TTS, embeddings, upscale, video.

Key comes from VENICE_API_KEY in .env (repo root) or the environment. Never hardcode it.
Every function takes model= so nothing is locked to a default. Run `python3 pipeline/venice.py list text`
(or image / tts / embedding / video / upscale) to see what the key can reach right now.

usage as a module:
    from pipeline.venice import chat, image, speak, embed, upscale, video

    chat("Write a hook about ghosting.", model="claude-opus-5-5")
    image("stick figure on a stage, flat vector", out="thumb.png", model="nano-banana-pro")
    speak("You are never going to make another close friend.", out="voice.mp3", voice="Rachel")
    embed(["line one", "line two"])
    upscale("thumb.png", out="thumb_2x.png", scale=2)
    video("a stick figure walks across a blank stage", out="clip.mp4", duration="5s", aspect_ratio="9:16")

usage as a smoke test:
    python3 pipeline/venice.py            # one cheap chat call
    python3 pipeline/venice.py list tts   # list models of a type
"""
import base64
import os
import sys
import time

import requests
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs  # noqa: E402  token/cost log, pipeline/costs.py

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(REPO_ROOT, ".env"))

BASE_URL = "https://api.venice.ai/api/v1"

# Defaults. Override with model= on any call.
TEXT_MODEL = "zai-org-glm-5-2"          # GLM 5.2
IMAGE_MODEL = "nano-banana-pro"
TTS_MODEL = "tts-elevenlabs-turbo-v2-5"
TTS_VOICE = "Rachel"
EMBED_MODEL = "text-embedding-bge-m3"
VIDEO_MODEL = "seedance-2-0-text-to-video-basic"

_key = os.environ.get("VENICE_API_KEY")
if not _key:
    sys.exit("VENICE_API_KEY is not set. Copy .env.example to .env and add the key.")

HEADERS = {"Authorization": f"Bearer {_key}"}
client = OpenAI(api_key=_key, base_url=BASE_URL)

# Venice prepends its own system prompt (~1.6k tokens) unless told not to.
# Reasoning models (GLM, DeepSeek, etc.) think first in message.reasoning_content, which counts
# against max_tokens, so leave room or the reply comes back empty.
NO_VENICE_PROMPT = {"venice_parameters": {"include_venice_system_prompt": False}}


def _post(path, timeout=300, **kw):
    r = requests.post(f"{BASE_URL}{path}", headers=HEADERS, timeout=timeout, **kw)
    if r.status_code != 200:
        raise RuntimeError(f"Venice {path} -> {r.status_code}: {r.text[:500]}")
    return r


def _save(data, out):
    if out:
        with open(out, "wb") as f:
            f.write(data)
        return out
    return data


# ---------- text ----------

def chat(prompt, system=None, model=TEXT_MODEL, max_tokens=2000, stage="other", short_dir=None,
         note="", **kwargs):
    """One-shot chat completion. Returns the reply text. Pass messages=[...] for multi-turn.
    Every call logs its exact token usage to <short_dir>/costs.jsonl under `stage` (see costs.py)."""
    messages = kwargs.pop("messages", None)
    if messages is None:
        messages = ([{"role": "system", "content": system}] if system else []) + [
            {"role": "user", "content": prompt}
        ]
    kwargs.setdefault("extra_body", NO_VENICE_PROMPT)
    t0 = time.time()
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, **kwargs)
    u = resp.usage
    costs.log(stage, model, u.prompt_tokens if u else 0, u.completion_tokens if u else 0,
              short_dir=short_dir, note=note, exact=bool(u), seconds=time.time() - t0)
    return resp.choices[0].message.content


# ---------- images ----------

def image(prompt, out=None, model=IMAGE_MODEL, size="1024x1536", fmt="png", **kwargs):
    """Text to image. Returns PNG/JPEG bytes, or the path if out= is given. size options:
    1024x1024, 1024x1536 (portrait, shorts), 1536x1024, 1024x1792, 1792x1024, auto."""
    body = {"model": model, "prompt": prompt, "size": size, "output_format": fmt,
            "response_format": "b64_json", **kwargs}
    r = _post("/images/generations", json=body)
    return _save(base64.b64decode(r.json()["data"][0]["b64_json"]), out)


def upscale(path_or_bytes, out=None, scale=2, creativity=0.01):
    """Upscale an image 2x or 4x. Returns PNG bytes, or the path if out= is given."""
    data = open(path_or_bytes, "rb").read() if isinstance(path_or_bytes, str) else path_or_bytes
    body = {"image": base64.b64encode(data).decode(), "scale": scale, "creativity": creativity}
    return _save(_post("/image/upscale", json=body).content, out)


# ---------- speech ----------

def speak(text, out=None, model=TTS_MODEL, voice=TTS_VOICE, fmt="mp3", speed=1.0,
          short_dir=None, note="", **kwargs):
    """Text to speech. Returns audio bytes, or the path if out= is given. Max 4096 chars per call.
    Voices depend on the model: ElevenLabs takes a name (Rachel, Aria) or a raw voice id;
    Kokoro takes af_sky / am_adam / etc; MiniMax takes DeepVoiceMan / WiseWoman; xAI takes eve / rex.
    Logs the character count (TTS is billed per character) to costs.jsonl under stage "voice"."""
    body = {"model": model, "input": text, "voice": voice, "response_format": fmt, "speed": speed, **kwargs}
    t0 = time.time()
    data = _post("/audio/speech", json=body).content
    costs.log("voice", model, chars=len(text), short_dir=short_dir, note=note, seconds=time.time() - t0)
    return _save(data, out)


# ---------- embeddings ----------

def embed(texts, model=EMBED_MODEL):
    """Returns one vector per input string."""
    if isinstance(texts, str):
        texts = [texts]
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


# ---------- video ----------

def video_quote(prompt, model=VIDEO_MODEL, duration="5s", **kwargs):
    """Price estimate before you queue a job."""
    body = {"model": model, "prompt": prompt, "duration": duration, **kwargs}
    return _post("/video/quote", json=body).json()


def video(prompt, out=None, model=VIDEO_MODEL, duration="5s", aspect_ratio="9:16",
          image_url=None, poll=10, timeout=1800, **kwargs):
    """Text (or image) to video. Queues the job, polls until done, returns MP4 bytes or the path.
    image_url can be an http(s) URL or a data: URL. Other model-specific fields (resolution, audio,
    negative_prompt, reference_image_urls, ...) pass straight through as kwargs."""
    body = {"model": model, "prompt": prompt, "duration": duration, "aspect_ratio": aspect_ratio, **kwargs}
    if image_url:
        body["image_url"] = image_url
    q = _post("/video/queue", json=body).json()
    qid, dl = q["queue_id"], q.get("download_url")
    t0 = time.time()
    while True:
        r = _post("/video/retrieve", json={"model": model, "queue_id": qid})
        if r.headers.get("content-type", "").startswith("video/"):
            return _save(r.content, out)
        st = r.json()
        if st.get("status") == "COMPLETED":
            if not dl:
                raise RuntimeError(f"video {qid} completed but no bytes or download_url")
            return _save(requests.get(dl, timeout=600).content, out)
        if time.time() - t0 > timeout:
            raise TimeoutError(f"video {qid} still {st.get('status')} after {timeout}s")
        time.sleep(poll)


# ---------- discovery ----------

def models(kind="text"):
    """kind: text, image, tts, embedding, upscale, video. Returns a list of model ids."""
    r = requests.get(f"{BASE_URL}/models", params={"type": kind}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return [m["id"] for m in r.json()["data"]]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print("\n".join(models(sys.argv[2] if len(sys.argv) > 2 else "text")))
    else:
        resp = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: Venice is working."}],
            max_tokens=400,
            extra_body=NO_VENICE_PROMPT,
        )
        print("model:", resp.model)
        print("reply:", resp.choices[0].message.content)
        print("usage:", resp.usage.prompt_tokens, "in /", resp.usage.completion_tokens, "out")
