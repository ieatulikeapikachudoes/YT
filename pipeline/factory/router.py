"""Router agent: a cheap model reads the live Venice catalog and assigns a model to every step."""
import json, venice
STEPS = {
  "topics":       "Brainstorm 10 short-video topics for a channel and pick a varied 5. Needs taste and some current awareness. Small output.",
  "research":     "Web research on one topic, return checkable facts with sources. Needs web search and accuracy. Medium output.",
  "script":       "Write and revise a 45-75s spoken script in a strict structure, punchy plain English. Writing quality matters most. Small output.",
  "script_judge": "Critically judge a script: logic, hook, claims, payoff; produce numbered change requests. Needs strong reasoning. Medium output.",
  "storyboard":   "Write 400-900 lines of JavaScript that build SVG scenes and GSAP animation beats from a provided helper kit. Needs strong coding and spatial layout. Large output.",
  "board_judge":  "Look at an image grid of storyboard frames and critique the visuals with specific fixes. MUST support vision. Medium output.",
  "package":      "Write a YouTube title/description, TikTok caption and cover headline. Small output, cheap.",
}
def main():
    cat = []
    for m in json.load(open("models.json"))["data"]:
        s = m.get("model_spec", {}); p = s.get("pricing", {}); c = s.get("capabilities", {})
        cat.append({"id": m["id"], "in": p.get("input", {}).get("usd"), "out": p.get("output", {}).get("usd"),
                    "vision": c.get("supportsVision"), "ctx": s.get("availableContextTokens")})
    prompt = f"""You are the model router for an automated short-video pipeline. Goal: lowest total cost while each step is still done well.
The owner prefers DeepSeek Flash models as the cheap default. Escalate to a pricier model only where quality clearly matters (writing, judging, code).
Never pick models priced above $5 per million output tokens. Never pick 'uncensored', 'heretic', 'abliterat', 'e2ee', 'role-play' or claude models.

Steps:
{json.dumps(STEPS, indent=1)}

Catalog (USD per million tokens):
{json.dumps(cat)}

Return JSON only: {{"<step>": {{"model": "<id>", "why": "<10 words>"}}, ...}} for every step."""
    r = venice.jsonish(venice.chat("deepseek-v4-pro", prompt, max_tokens=3000, temperature=0.2, tag="router"))
    ids = {c["id"]: c for c in cat}
    for k in STEPS:
        m = r.get(k, {}).get("model")
        if m not in ids or (k == "board_judge" and not ids[m]["vision"]) or (ids[m]["out"] or 99) > 5:
            r[k] = {"model": "deepseek-v4-1-flash" if k == "board_judge" else "deepseek-v4-flash", "why": "fallback: router pick invalid"}
    json.dump(r, open("routing.json", "w"), indent=1)
    for k, v in r.items(): print(f"{k:13s} {v['model']:28s} {v['why']}")
main()
