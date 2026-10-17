"""Fit one (R, S, T) type vector per Track B record from its HISTORY games only (leave-target-out),
using the model's type table. Output: outputs/track_b/<model>/fits.jsonl with {record_idx, type_vector, fit_error, n_history}.

Fit rule (Jackson et al. 2026, Sec. 4.2.1 / 4.2.3): for each candidate type, the mean over the
subject's history games of |observed - median of the type's sampled choices| / action range; pick the
minimum; ties -> all tied vectors recorded, first used.
"""
from __future__ import annotations
import argparse, collections, json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.games import LABEL2ROLE, RANGE

ap = argparse.ArgumentParser(); ap.add_argument("--model", default="gemini-3.5-flash"); a = ap.parse_args()
table = collections.defaultdict(list)  # (vector key, role) -> choices
for l in Path(f"outputs/type_table/{a.model}.jsonl").read_text().splitlines():
    d = json.loads(l)
    if d["choice"] is not None:
        table[(json.dumps(d["type_vector"], sort_keys=True), d["role"])].append(d["choice"])
med = {k: statistics.median(v) for k, v in table.items()}
vectors = sorted({k[0] for k in med})
recs = [json.loads(l) for l in Path("data/track_b_subjects.jsonl").read_text().splitlines()]
out = Path(f"outputs/track_b/{a.model}/fits.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
n_fit = 0
with open(out, "w") as f:
    for i, rec in enumerate(recs):
        obs = []
        for h in rec["history"]:
            role = LABEL2ROLE[h["label"]]
            try:
                obs.append((role, float(h["choice"])))
            except ValueError:
                pass
        if not obs:
            continue
        scored = []
        for vk in vectors:
            errs = [abs(v - med[(vk, role)]) / (RANGE[role][1] - RANGE[role][0]) for role, v in obs if (vk, role) in med]
            if len(errs) == len(obs):
                scored.append((sum(errs) / len(errs), vk))
        if not scored:
            continue
        scored.sort(); best_err = scored[0][0]; ties = [vk for e, vk in scored if e == best_err]
        f.write(json.dumps({"record_idx": i, "type_vector": json.loads(ties[0]), "ties": len(ties),
                            "fit_error": best_err, "n_history": len(obs)}) + "\n"); n_fit += 1
print(f"fitted {n_fit}/{len(recs)} records -> {out}")
