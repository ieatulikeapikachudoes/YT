"""Cost breakdown per stage from costs.jsonl files.

    python3 pipeline/cost_report.py pipeline/opus/shorts/law46            # one short
    python3 pipeline/cost_report.py pipeline/opus/shorts/*                # a batch, summed
    python3 pipeline/cost_report.py --json ...                            # machine readable

Prints tokens in/out, dollars, and share of total per stage. Rows marked "est" were estimated
(session work at 4 chars per token), everything else came back from an API.
"""
import glob
import json
import os
import sys

from costs import STAGES  # noqa: E402  (run from pipeline/ or via python3 pipeline/cost_report.py)


def load(paths):
    rows = []
    for p in paths:
        f = p if p.endswith(".jsonl") else os.path.join(p, "costs.jsonl")
        if not os.path.exists(f):
            sys.stderr.write(f"no costs.jsonl in {p}\n")
            continue
        for line in open(f):
            line = line.strip()
            if line:
                r = json.loads(line)
                r["_short"] = os.path.basename(os.path.dirname(f) or ".")
                rows.append(r)
    return rows


def summarize(rows):
    by = {}
    for r in rows:
        s = by.setdefault(r["stage"], {"calls": 0, "in": 0, "out": 0, "usd": 0.0, "unpriced": 0, "est": 0, "models": set()})
        s["calls"] += 1
        s["in"] += r.get("in", 0) or 0
        s["out"] += r.get("out", 0) or 0
        if r.get("usd") is None:
            s["unpriced"] += 1
        else:
            s["usd"] += r["usd"]
        if not r.get("exact", True):
            s["est"] += 1
        s["models"].add(r.get("model", "?"))
    return by


def report(rows, as_json=False):
    by = summarize(rows)
    total_usd = sum(s["usd"] for s in by.values())
    total_tok = sum(s["in"] + s["out"] for s in by.values())
    shorts = sorted({r["_short"] for r in rows})
    order = [s for s in STAGES if s in by] + [s for s in by if s not in STAGES]
    if as_json:
        out = {k: {**v, "models": sorted(v["models"])} for k, v in by.items()}
        print(json.dumps({"shorts": shorts, "stages": out, "total_usd": round(total_usd, 4),
                          "total_tokens": total_tok}, indent=1))
        return
    print(f"shorts: {', '.join(shorts)}  ({len(shorts)})")
    print(f"{'stage':<13}{'calls':>6}{'in':>10}{'out':>9}{'usd':>9}{'% usd':>7}{'% tok':>7}  models")
    for k in order:
        s = by[k]
        pct_usd = (s["usd"] / total_usd * 100) if total_usd else 0
        pct_tok = ((s["in"] + s["out"]) / total_tok * 100) if total_tok else 0
        flags = []
        if s["est"]:
            flags.append(f"est x{s['est']}")
        if s["unpriced"]:
            flags.append(f"no price x{s['unpriced']}")
        print(f"{k:<13}{s['calls']:>6}{s['in']:>10,}{s['out']:>9,}{s['usd']:>9.3f}{pct_usd:>6.0f}%{pct_tok:>6.0f}%  "
              f"{', '.join(sorted(s['models']))}" + (f"  [{'; '.join(flags)}]" if flags else ""))
    print(f"{'total':<13}{sum(s['calls'] for s in by.values()):>6}{sum(s['in'] for s in by.values()):>10,}"
          f"{sum(s['out'] for s in by.values()):>9,}{total_usd:>9.3f}")
    if shorts:
        print(f"per short: ${total_usd / len(shorts):.3f}, {total_tok // len(shorts):,} tokens")
    if any(s["unpriced"] for s in by.values()):
        print("some rows have no price: fill pipeline/prices.json or run `python3 pipeline/costs.py prices`")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--json"]
    paths = [p for a in args for p in (glob.glob(a) or [a])]
    if not paths:
        sys.exit(__doc__)
    report(load(paths), as_json="--json" in sys.argv)
