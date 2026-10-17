"""Score Track B outputs: individual MAE (normalized 0-100) / accuracy (push_pull) and Wasserstein W per game,
per condition, stratified by history size. Prints a table and writes outputs/track_b/<model>/summary.json."""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.games import ROLES, RANGE, normalize

ap = argparse.ArgumentParser(); ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--min-history", type=int, default=1); ap.add_argument("--conditions", nargs="*"); a = ap.parse_args()
d = Path(f"outputs/track_b/{a.model}")
conds = a.conditions or [p.stem for p in sorted(d.glob("*.jsonl")) if p.stem not in ("fits",)]
rows = {c: [json.loads(l) for l in (d / f"{c}.jsonl").read_text().splitlines()] for c in conds}
# restrict to records present in every condition (fair comparison) and with enough history
common = set.intersection(*[{r["record_idx"] for r in v} for v in rows.values()])
summary = {}
print(f"model={a.model}  min_history={a.min_history}  records={len(common)}")
print(f"{'game':20s} {'cond':24s} {'n':>5s} {'MAE/acc':>8s} {'W':>7s} {'sd_ratio':>8s} {'unparsed':>8s}")
for game in ROLES:
    for c in conds:
        rs = [r for r in rows[c] if r["record_idx"] in common and r["target_game"] == game and r["history_count"] >= a.min_history]
        if not rs: continue
        unp = sum(r["prediction"] is None for r in rs)
        if game == "push_pull":
            ok = [r for r in rs if r["prediction"] is not None]
            acc = np.mean([r["prediction"] == r["truth"] for r in ok]) if ok else float("nan")
            ph = np.mean([r["truth"] == "Push" for r in rs]); pm = np.mean([r["prediction"] == "Push" for r in ok]) if ok else float("nan")
            summary[(game, c)] = {"n": len(rs), "acc": acc, "push_rate_human": ph, "push_rate_model": pm, "unparsed": unp}
            print(f"{game:20s} {c:24s} {len(rs):5d} {acc:8.3f} {'-':>7s} {'-':>8s} {unp:8d}")
            continue
        ok = [r for r in rs if r["prediction"] is not None]
        t = np.array([normalize(float(r["truth"]), game) for r in ok]); p = np.array([normalize(r["prediction"], game) for r in ok])
        mae = float(np.mean(np.abs(t - p))) if len(ok) else float("nan")
        W = float(wasserstein_distance(t, p)) if len(ok) else float("nan")
        sd = float(p.std() / t.std()) if len(ok) and t.std() > 0 else float("nan")
        summary[(game, c)] = {"n": len(rs), "mae": mae, "W": W, "sd_ratio": sd, "unparsed": unp}
        print(f"{game:20s} {c:24s} {len(rs):5d} {mae:8.2f} {W:7.2f} {sd:8.2f} {unp:8d}")
# averages across numeric games
print("\nmean over numeric games:")
for c in conds:
    ms = [v["mae"] for (g, cc), v in summary.items() if cc == c and "mae" in v]; ws = [v["W"] for (g, cc), v in summary.items() if cc == c and "W" in v]
    if ms: print(f"  {c:24s} MAE={np.mean(ms):6.2f}  W={np.mean(ws):6.2f}")
(d / "summary.json").write_text(json.dumps({f"{g}|{c}": v for (g, c), v in summary.items()}, indent=1))
