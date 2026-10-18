"""Stronger supervised ceiling: train on records 1000.. of a larger build (same shuffle seed, so records 0..999 are
exactly the suite subjects), using every item of every training record as a target; evaluate on the suite records.
Pooled HistGBT with target-item id as a categorical feature. Inputs: demographics / traits / history / combos."""
from __future__ import annotations
import argparse, json, collections
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
from sklearn.ensemble import HistGradientBoostingClassifier
ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--max-train-examples", type=int, default=250000); a = ap.parse_args()
test = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()]
train = [json.loads(l) for l in Path(f"data/suite_train/{a.dataset}.jsonl").read_text().splitlines()][len(test):]
test_ids = {r["subject_id"] for r in test}; train = [r for r in train if r["subject_id"] not in test_ids]
items = sorted({k for r in test + train for k in r["items"]}); item_ix = {k: i for i, k in enumerate(items)}
demo_keys = sorted({k for r in test for k, _ in r["demographics"]}); enc_tab = collections.defaultdict(dict)
trait_keys = sorted({k for r in test if r.get("traits") for k in r["traits"]})
def feats(r, target, kind):
    x = [item_ix[target]]
    if "demographics" in kind:
        d = dict(r["demographics"])
        for k in demo_keys:
            v = d.get(k)
            if v is None: x.append(np.nan); continue
            try: x.append(float(v))
            except ValueError: x.append(enc_tab[k].setdefault(v, len(enc_tab[k])))
    if "traits" in kind:
        t = r.get("traits") or {}
        for k in trait_keys:
            v = t.get(k); x.append(float(v) if isinstance(v, (int, float)) else (enc_tab["T:" + k].setdefault(v, len(enc_tab["T:" + k])) if v is not None else np.nan))
    if "history" in kind:
        x += [r["items"][k]["answer"] if (k in r["items"] and k != target) else np.nan for k in items]
    return x
rng = np.random.default_rng(0)
pairs = [(r, k) for r in train for k in r["items"]]
if len(pairs) > a.max_train_examples: pairs = [pairs[i] for i in rng.choice(len(pairs), a.max_train_examples, replace=False)]
y_te = np.array([r["items"][r["target_item"]]["answer"] for r in test]); lo = np.array([r["scale"]["min"] for r in test]); hi = np.array([r["scale"]["max"] for r in test])
norm = lambda v: 100.0 * (v - lo) / np.maximum(1, hi - lo)
kinds = ["none", "demographics", "history", "demographics+history"] + (["traits", "demographics+traits"] if trait_keys else [])
print(f"{a.dataset}: train subjects {len(train)}, train examples {len(pairs)}, test {len(test)}, items {len(items)}", flush=True)
print(f"{'input':24s} {'acc':>6s} {'nMAE':>6s} {'W(item)':>8s}"); out = {}
y_tr = np.array([r["items"][k]["answer"] for r, k in pairs])
for kind in kinds:
    X_tr = np.array([feats(r, k, kind) for r, k in pairs], dtype=float); X_te = np.array([feats(r, r["target_item"], kind) for r in test], dtype=float)
    cat = [True] + [False] * (X_tr.shape[1] - 1)
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, categorical_features=cat, random_state=0).fit(X_tr, y_tr); pred = m.predict(X_te)
    acc = float(np.mean(pred == y_te)); nm = float(np.mean(np.abs(norm(pred) - norm(y_te))))
    by = collections.defaultdict(lambda: ([], []))
    for r, t, p in zip(test, norm(y_te), norm(pred)): by[r["target_item"]][0].append(t); by[r["target_item"]][1].append(p)
    ws = [wasserstein_distance(t, p) for t, p in by.values() if len(t) >= 5]; w = float(np.mean(ws)) if ws else float("nan")
    out[kind] = {"acc": acc, "nmae": nm, "W_item": w}; print(f"{kind:24s} {acc:6.3f} {nm:6.2f} {w:8.2f}", flush=True)
Path(f"outputs/suite/{a.dataset}/ceiling.json").write_text(json.dumps(out, indent=1))
