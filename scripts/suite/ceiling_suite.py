"""Supervised ceiling for a suite dataset without an LLM: pooled HistGradientBoosting classifier over the 1,000 suite
records (5-fold CV), with the target item id as a categorical feature plus the input system's features.
Inputs: demographics (ordinal-encoded strings), traits, history (answers to the other items, NaN where absent), combos.
This is a conservative ceiling (1,000 records only); per-item models on the full raw files would be higher."""
from __future__ import annotations
import argparse, json, collections
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import KFold
ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); a = ap.parse_args()
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()]
items = sorted({k for r in recs for k in r["items"]}); item_ix = {k: i for i, k in enumerate(items)}
if len(items) > 300:  # SocSci210: per-record item ids are not shared; use target position only
    items = ["s%d" % i for i in range(12)]; item_ix = {k: i for i, k in enumerate(items)}
demo_keys = sorted({k for r in recs for k, _ in r["demographics"]}); demo_vals = {k: {} for k in demo_keys}
trait_keys = sorted({k for r in recs if r.get("traits") for k in r["traits"]})
def enc(r, kind):
    x = [item_ix.get(r["target_item"], -1)]
    if "demographics" in kind:
        d = dict(r["demographics"])
        for k in demo_keys:
            v = d.get(k); 
            if v is None: x.append(np.nan); continue
            try: x.append(float(v))
            except ValueError: x.append(demo_vals[k].setdefault(v, len(demo_vals[k])))
    if "traits" in kind:
        t = r.get("traits") or {}
        for k in trait_keys:
            v = t.get(k); x.append(float(v) if isinstance(v, (int, float)) else (demo_vals.setdefault("T:" + k, {}).setdefault(v, len(demo_vals.get("T:" + k, {}))) if v is not None else np.nan))
    if "history" in kind:
        x += [r["items"][k]["answer"] if (k in r["items"] and k != r["target_item"]) else np.nan for k in items]
    return x
y = np.array([r["items"][r["target_item"]]["answer"] for r in recs]); lo = np.array([r["scale"]["min"] for r in recs]); hi = np.array([r["scale"]["max"] for r in recs])
norm = lambda v: 100.0 * (v - lo) / np.maximum(1, hi - lo)
out = {}; kinds = ["none", "demographics", "history", "demographics+history"] + (["traits", "demographics+traits"] if trait_keys else [])
print(f"{a.dataset}: {len(recs)} records, {len(items)} items, {len(demo_keys)} demo fields, {len(trait_keys)} traits")
print(f"{'input':24s} {'acc':>6s} {'nMAE':>6s} {'W(item)':>8s}")
for kind in kinds:
    X = np.array([enc(r, kind) for r in recs], dtype=float); pred = np.zeros(len(recs), dtype=int)
    cat = [True] + [False] * (X.shape[1] - 1)
    for tr, te in KFold(5, shuffle=True, random_state=0).split(X):
        m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, categorical_features=cat if X.shape[1] > 1 else None, random_state=0).fit(X[tr], y[tr]); pred[te] = m.predict(X[te])
    acc = float(np.mean(pred == y)); nm = float(np.mean(np.abs(norm(pred) - norm(y))))
    by = collections.defaultdict(lambda: ([], []))
    for r, t, p in zip(recs, norm(y), norm(pred)): by[r["target_item"]][0].append(t); by[r["target_item"]][1].append(p)
    ws = [wasserstein_distance(t, p) for t, p in by.values() if len(t) >= 5]; w = float(np.mean(ws)) if ws else float("nan")
    out[kind] = {"acc": acc, "nmae": nm, "W_item": w}; print(f"{kind:24s} {acc:6.3f} {nm:6.2f} {w:8.2f}", flush=True)
Path(f"outputs/suite/{a.dataset}").mkdir(parents=True, exist_ok=True); Path(f"outputs/suite/{a.dataset}/ceiling.json").write_text(json.dumps(out, indent=1))
