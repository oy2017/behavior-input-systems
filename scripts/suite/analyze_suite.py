"""Score suite conditions for one dataset: accuracy, normalized MAE (0-100), W per target item (normalized), sd ratio."""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--conditions", nargs="*"); a = ap.parse_args()
d = Path(f"outputs/suite/{a.dataset}/{a.model}")
conds = a.conditions or [p.stem for p in sorted(d.glob("*.jsonl")) if p.stem != "fits"]
rows = {c: [json.loads(l) for l in (d / f"{c}.jsonl").read_text().splitlines()] for c in conds}
common = set.intersection(*[{r["record_idx"] for r in v} for v in rows.values()])
def norm(v, r): return 100.0 * (v - r["lo"]) / max(1, r["hi"] - r["lo"])
print(f"dataset={a.dataset} model={a.model} records={len(common)}")
print(f"{'cond':24s} {'acc':>6s} {'nMAE':>6s} {'W(item)':>8s} {'sd_ratio':>8s} {'unparsed':>8s}")
summary = {}
for c in conds:
    rs = [r for r in rows[c] if r["record_idx"] in common]; ok = [r for r in rs if r["prediction"] is not None]
    t = np.array([norm(r["truth"], r) for r in ok]); p = np.array([norm(r["prediction"], r) for r in ok])
    acc = float(np.mean([r["truth"] == r["prediction"] for r in ok])); mae = float(np.mean(np.abs(t - p)))
    by = collections.defaultdict(lambda: ([], []))
    for r, tt, pp in zip(ok, t, p): by[r["target_item"]][0].append(tt); by[r["target_item"]][1].append(pp)
    ws = [wasserstein_distance(tt, pp) for tt, pp in by.values() if len(tt) >= 5]
    w = float(np.mean(ws)) if ws else float(wasserstein_distance(t, p)); sd = float(p.std() / t.std()) if t.std() > 0 else float("nan")
    summary[c] = {"n": len(rs), "acc": acc, "nmae": mae, "W_item": w, "sd_ratio": sd, "unparsed": len(rs) - len(ok), "items_scored": len(ws)}
    print(f"{c:24s} {acc:6.3f} {mae:6.2f} {w:8.2f} {sd:8.2f} {len(rs)-len(ok):8d}")
(d / "summary.json").write_text(json.dumps(summary, indent=1))
