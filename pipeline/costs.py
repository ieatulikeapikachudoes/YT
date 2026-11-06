"""Token and cost log for every stage of a short.

One file per short: <short dir>/costs.jsonl, one line per model call or stage.
Set COSTS_FILE to point somewhere else (a batch-wide file, say).

Two kinds of rows:
  exact      the API returned the usage (Venice chat, Venice TTS, Agent subagents that report usage)
  estimated  the work happened in the Claude session itself (Opus reading the kit, writing scenes.js).
             Tokens are estimated at 4 chars per token from what was read and written.

From code:
    from pipeline.costs import log, log_files, est_tokens
    log("script", "claude-opus-5-5", tokens_in=12000, tokens_out=800, short_dir=d, note="judge S round 1")
    log_files("board", "claude-opus-5-5", read=["kit/kit.html", "script-A.json"], wrote=["scenes.js", "beats.js"], short_dir=d)

From the shell (what Opus does between stages):
    python3 pipeline/costs.py log <short-dir> <stage> <model> <tokens_in> <tokens_out> [--note "..."] [--estimated] [--usd 0.012]
    python3 pipeline/costs.py files <short-dir> <stage> <model> --read a b --wrote c d [--note "..."]
    python3 pipeline/costs.py prices               # refresh Venice prices into pipeline/prices.json (needs the key)

Prices live in pipeline/prices.json: usd per million tokens (in, out), or per million characters for TTS.
Never log prompts, replies, or keys. Only counts.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PRICES_FILE = os.path.join(HERE, "prices.json")
CHARS_PER_TOKEN = 4

STAGES = ["pick", "research", "script", "script_judge", "voice", "board", "board_judge",
          "render", "package", "final_judge", "other"]


def _prices():
    if os.path.exists(PRICES_FILE):
        return json.load(open(PRICES_FILE))
    return {}


def price(model, tokens_in=0, tokens_out=0, chars=0):
    """USD for a call. Returns None if the model has no price yet."""
    p = _prices().get(model)
    if not p:
        return None
    if "per_m_chars" in p:
        return chars / 1e6 * p["per_m_chars"]
    return tokens_in / 1e6 * p.get("in", 0) + tokens_out / 1e6 * p.get("out", 0)


def est_tokens(text_or_path):
    """Rough token count: 4 chars per token. Takes a string or a file path."""
    if isinstance(text_or_path, str) and os.path.exists(text_or_path):
        n = os.path.getsize(text_or_path)
    else:
        n = len(text_or_path.encode("utf-8")) if isinstance(text_or_path, str) else len(text_or_path)
    return round(n / CHARS_PER_TOKEN)


def costs_path(short_dir=None):
    if os.environ.get("COSTS_FILE"):
        return os.environ["COSTS_FILE"]
    return os.path.join(short_dir or ".", "costs.jsonl")


def log(stage, model, tokens_in=0, tokens_out=0, short_dir=None, note="", usd=None,
        exact=True, chars=0, seconds=None):
    """Append one row. usd is computed from prices.json unless given."""
    if stage not in STAGES:
        sys.stderr.write(f"costs: unknown stage {stage!r}, logging under 'other'\n")
        stage = "other"
    if usd is None:
        usd = price(model, tokens_in, tokens_out, chars)
    row = {
        "t": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stage": stage,
        "model": model,
        "in": int(tokens_in),
        "out": int(tokens_out),
        "usd": round(usd, 5) if usd is not None else None,
        "exact": bool(exact),
        "note": note,
    }
    if chars:
        row["chars"] = int(chars)
    if seconds is not None:
        row["seconds"] = round(seconds, 1)
    path = costs_path(short_dir)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def log_files(stage, model, read=(), wrote=(), short_dir=None, note="", overhead_in=0):
    """Estimate a session stage from what was read (input) and written (output).
    overhead_in: extra input tokens to add for the prompt around the files (brief, playbook)."""
    tin = sum(est_tokens(p) for p in read) + overhead_in
    tout = sum(est_tokens(p) for p in wrote)
    n = note or f"read {len(read)} files, wrote {len(wrote)} files"
    return log(stage, model, tin, tout, short_dir=short_dir, note=n, exact=False)


def refresh_venice_prices():
    """Pull Venice model prices into prices.json. Needs VENICE_API_KEY. Keeps non-Venice entries."""
    import requests
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(HERE), ".env"))
    key = os.environ.get("VENICE_API_KEY")
    if not key:
        sys.exit("VENICE_API_KEY not set")
    prices = _prices()
    n = 0
    for kind in ("text", "tts"):
        r = requests.get("https://api.venice.ai/api/v1/models", params={"type": kind},
                         headers={"Authorization": f"Bearer {key}"}, timeout=60)
        r.raise_for_status()
        for m in r.json()["data"]:
            pr = m.get("model_spec", {}).get("pricing", {}) or {}
            entry = {"source": "venice"}
            if "input" in pr or "output" in pr:
                entry["in"] = pr.get("input", {}).get("usd", 0)
                entry["out"] = pr.get("output", {}).get("usd", 0)
            if "characters" in pr:
                entry["per_m_chars"] = pr["characters"].get("usd", 0)
            if len(entry) > 1:
                prices[m["id"]] = entry
                n += 1
    json.dump(prices, open(PRICES_FILE, "w"), indent=1, sort_keys=True)
    print(f"wrote {n} Venice prices to {PRICES_FILE}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("log")
    a.add_argument("short_dir"); a.add_argument("stage"); a.add_argument("model")
    a.add_argument("tokens_in", type=int); a.add_argument("tokens_out", type=int)
    a.add_argument("--note", default=""); a.add_argument("--estimated", action="store_true")
    a.add_argument("--usd", type=float, default=None)
    b = sub.add_parser("files")
    b.add_argument("short_dir"); b.add_argument("stage"); b.add_argument("model")
    b.add_argument("--read", nargs="*", default=[]); b.add_argument("--wrote", nargs="*", default=[])
    b.add_argument("--note", default=""); b.add_argument("--overhead", type=int, default=0)
    sub.add_parser("prices")
    args = ap.parse_args()
    if args.cmd == "log":
        print(json.dumps(log(args.stage, args.model, args.tokens_in, args.tokens_out, args.short_dir,
                             args.note, args.usd, exact=not args.estimated)))
    elif args.cmd == "files":
        print(json.dumps(log_files(args.stage, args.model, args.read, args.wrote, args.short_dir,
                                   args.note, args.overhead)))
    elif args.cmd == "prices":
        refresh_venice_prices()


if __name__ == "__main__":
    main()
