"""Venice AI client. OpenAI-compatible, so it is the openai package pointed at Venice.

Key comes from VENICE_API_KEY in .env (repo root) or the environment. Never hardcode it.

usage as a module:
    from pipeline.venice import client, chat, MODEL
    print(chat("Say hi in five words."))

usage as a smoke test:
    python3 pipeline/venice.py
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(REPO_ROOT, ".env"))

BASE_URL = "https://api.venice.ai/api/v1"
MODEL = "zai-org-glm-5-2"  # GLM 5.2

_key = os.environ.get("VENICE_API_KEY")
if not _key:
    sys.exit("VENICE_API_KEY is not set. Copy .env.example to .env and add the key.")

client = OpenAI(api_key=_key, base_url=BASE_URL)


def chat(prompt, system=None, model=MODEL, **kwargs):
    """One-shot chat completion. Returns the reply text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    return resp.choices[0].message.content


if __name__ == "__main__":
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Reply with exactly: Venice is working."}],
        max_tokens=20,
    )
    print("model:", resp.model)
    print("reply:", resp.choices[0].message.content)
    print("usage:", resp.usage.prompt_tokens, "in /", resp.usage.completion_tokens, "out")
