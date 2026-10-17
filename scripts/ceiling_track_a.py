"""Supervised information ceiling for Track A (no LLM): predict the target item answer from each input system
using HistGradientBoosting, trained on the ~18.7k raw BIG5 respondents NOT in the Track A subject set and
evaluated on the 997 Track A records (same target item per record). Inputs: demographics, big_five, the other
49 answers, and combinations. Also: majority-class and per-item-mode baselines, and the W floor."""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
from sklearn.ensemble import HistGradientBoostingClassifier
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.subjects import COLS, big_five_scores

with open("data/big5_raw/BIG5/data.csv", encoding="utf-8", errors="replace") as f:
    raw = list(csv.DictReader(f, delimiter="\t"))
recs = [json.loads(l) for l in Path("data/track_a_subjects.jsonl").read_text().splitlines()]
test_rows = {r["raw_row"] for r in recs}
def feats(row, answers, kind, target):
    x = []
    if "demographics" in kind: x += [float(row["age"]), float(row["gender"]), float(row["race"]), float(row["hand"]), float(row["engnat"]), float(hash(row["country"]) % 1000)]
    if "big_five" in kind: x += list(big_five_scores(answers).values())
    if "history" in kind: x += [answers[c] if c != target else np.nan for c in COLS]
    return x
train = [(i, r) for i, r in enumerate(raw) if i not in test_rows and all(r[c].isdigit() and r[c] != "0" for c in COLS) and r["age"].isdigit() and int(r["age"]) < 100]
print(f"train respondents {len(train)}, test records {len(recs)}")
y_test = np.array([r["target_answer"] for r in recs])
items = sorted({r["target_item"] for r in recs}); out = {}
print(f"{'input':24s} {'acc':>6s} {'MAE':>6s} {'W(item)':>8s}")
# baselines
maj = {it: max(range(1, 6), key=lambda v: sum(1 for i, r in train if int(r[it]) == v)) for it in items}
pred = np.array([maj[r["target_item"]] for r in recs])
print(f"{'per-item mode':24s} {np.mean(pred==y_test):6.3f} {np.mean(np.abs(pred-y_test)):6.3f} {'-':>8s}")
for kind in ["demographics", "big_five", "history", "demographics+big_five", "demographics+history"]:
    pred = np.zeros(len(recs), dtype=int)
    for it in items:
        idx = [k for k, r in enumerate(recs) if r["target_item"] == it]
        Xtr = np.array([feats(r, {c: int(r[c]) for c in COLS}, kind, it) for i, r in train]); ytr = np.array([int(r[it]) for i, r in train])
        m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, random_state=0).fit(Xtr, ytr)
        Xte = np.array([feats(raw[recs[k]["raw_row"]], recs[k]["answers"], kind, it) for k in idx]); pred[idx] = m.predict(Xte)
    acc = float(np.mean(pred == y_test)); mae = float(np.mean(np.abs(pred - y_test)))
    w = float(np.mean([wasserstein_distance(y_test[[k for k, r in enumerate(recs) if r["target_item"] == it]], pred[[k for k, r in enumerate(recs) if r["target_item"] == it]]) for it in items if sum(r["target_item"] == it for r in recs) >= 5]))
    out[kind] = {"acc": acc, "mae": mae, "W_item": w}; print(f"{kind:24s} {acc:6.3f} {mae:6.3f} {w:8.3f}", flush=True)
Path("outputs/track_a/ceiling.json").write_text(json.dumps(out, indent=1))
