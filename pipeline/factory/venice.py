"""Thin Venice client. Key comes from .env (never printed). Every call is logged to costs.jsonl."""
import os, json, time, base64, urllib.request, urllib.error, re
HERE = os.path.dirname(os.path.abspath(__file__))
def _key():
    for line in open(os.path.join(HERE, ".env")):
        if line.startswith("VENICE_API_KEY="): return line.split("=", 1)[1].strip()
PRICES = {}
def _prices():
    if PRICES: return PRICES
    p = os.path.join(HERE, "models.json")
    if os.path.exists(p):
        for m in json.load(open(p))["data"]:
            pr = m.get("model_spec", {}).get("pricing", {})
            PRICES[m["id"]] = (pr.get("input", {}).get("usd", 0), pr.get("output", {}).get("usd", 0))
    return PRICES

def chat(model, prompt, system=None, images=(), web=False, think=False, max_tokens=8000, temperature=0.7, tag=""):
    content = prompt
    if images:
        content = [{"type": "text", "text": prompt}]
        for im in images:
            b = base64.b64encode(open(im, "rb").read()).decode()
            mime = "image/png" if im.endswith(".png") else "image/jpeg"
            content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b}"}})
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": content}]
    body = {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature,
            "venice_parameters": {"include_venice_system_prompt": False, "disable_thinking": not think,
                                  "strip_thinking_response": True, "enable_web_search": "on" if web else "off"}}
    for attempt in range(4):
        try:
            req = urllib.request.Request("https://api.venice.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                         headers={"Authorization": "Bearer " + _key(), "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=600))
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if attempt == 3: raise RuntimeError(f"venice {e.code}: {msg}")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            if attempt == 3: raise
            time.sleep(5 * (attempt + 1))
    out = d["choices"][0]["message"].get("content") or ""
    out = re.sub(r"<think>.*?</think>", "", out, flags=re.S).strip()
    u = d.get("usage", {}); pi, po = _prices().get(model, (0, 0))
    cost = u.get("prompt_tokens", 0) / 1e6 * pi + u.get("completion_tokens", 0) / 1e6 * po
    with open(os.path.join(HERE, "costs.jsonl"), "a") as f:
        f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "tag": tag, "model": model, "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"), "usd": round(cost, 5)}) + "\n")
    return out

def block(text, lang=None):
    """Pull the first fenced block (optionally of a language) out of a reply."""
    m = re.search(r"```" + (lang or r"[a-zA-Z]*") + r"\s*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()

def jsonish(text):
    t = block(text, "json") if "```" in text else text
    t = t[t.find("{") if "{" in t and (t.find("[") < 0 or t.find("{") < t.find("[")) else t.find("["):]
    return json.loads(t[: max(t.rfind("}"), t.rfind("]")) + 1])
