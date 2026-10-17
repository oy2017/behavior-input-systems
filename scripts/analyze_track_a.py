"""Score Track A: accuracy and MAE on the 1-5 scale (individual), W per target item averaged over items,
sd ratio. Prints a table and writes outputs/track_a/<model>/summary.json."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
ap = argparse.ArgumentParser(); ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--conditions", nargs="*"); a = ap.parse_args()
d = Path(f"outputs/track_a/{a.model}")
conds = a.conditions or [p.stem for p in sorted(d.glob("*.jsonl")) if not p.stem.startswith("fits")]
rows = {c: [json.loads(l) for l in (d / f"{c}.jsonl").read_text().splitlines()] for c in conds}
common = set.intersection(*[{r["record_idx"] for r in v} for v in rows.values()])
print(f"model={a.model} records={len(common)}")
print(f"{'cond':26s} {'acc':>6s} {'MAE':>6s} {'W(item-avg)':>11s} {'W(pooled)':>9s} {'sd_ratio':>8s} {'unparsed':>8s}")
summary = {}
for c in conds:
    rs = [r for r in rows[c] if r["record_idx"] in common]; ok = [r for r in rs if r["prediction"] is not None]
    t = np.array([r["truth"] for r in ok]); p = np.array([r["prediction"] for r in ok])
    acc = float(np.mean(t == p)); mae = float(np.mean(np.abs(t - p)))
    by_item = collections.defaultdict(lambda: ([], []))
    for r in ok: by_item[r["target_item"]][0].append(r["truth"]); by_item[r["target_item"]][1].append(r["prediction"])
    w_item = float(np.mean([wasserstein_distance(tt, pp) for tt, pp in by_item.values() if len(tt) >= 5]))
    w_pool = float(wasserstein_distance(t, p)); sd = float(p.std() / t.std())
    summary[c] = {"n": len(rs), "acc": acc, "mae": mae, "W_item": w_item, "W_pooled": w_pool, "sd_ratio": sd, "unparsed": len(rs) - len(ok)}
    print(f"{c:26s} {acc:6.3f} {mae:6.3f} {w_item:11.3f} {w_pool:9.3f} {sd:8.2f} {len(rs)-len(ok):8d}")
(d / "summary.json").write_text(json.dumps(summary, indent=1))
