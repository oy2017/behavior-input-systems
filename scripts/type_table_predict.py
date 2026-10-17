"""Pseudo-condition `type_table`: predict the target choice directly from the type table (no new LLM call),
exactly as Jackson et al. 2026 Sec. 4.2.3: fit on history games, predict the held-out game with the median
of the fitted type's sampled choices; ties averaged. Writes outputs/track_b/<model>/type_table.jsonl in the
same format as the LLM conditions so analyze_track_b.py can score it."""
from __future__ import annotations
import argparse, collections, json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.games import LABEL2ROLE, RANGE

ap = argparse.ArgumentParser(); ap.add_argument("--model", default="gemini-3.5-flash"); a = ap.parse_args()
table = collections.defaultdict(list)
for l in Path(f"outputs/type_table/{a.model}.jsonl").read_text().splitlines():
    d = json.loads(l)
    if isinstance(d["choice"], (int, float)):
        table[(json.dumps(d["type_vector"], sort_keys=True), d["role"])].append(d["choice"])
    elif d["role"] == "push_pull" and d["choice"] in ("Push", "Pull"):
        table[(json.dumps(d["type_vector"], sort_keys=True), d["role"])].append(1.0 if d["choice"] == "Push" else 0.0)
med = {k: statistics.median(v) for k, v in table.items()}
vectors = sorted({k[0] for k in med})
recs = [json.loads(l) for l in Path("data/track_b_subjects.jsonl").read_text().splitlines()]
out = Path(f"outputs/track_b/{a.model}/type_table.jsonl"); n = 0
with open(out, "w") as f:
    for i, rec in enumerate(recs):
        obs = []
        for h in rec["history"]:
            try: obs.append((LABEL2ROLE[h["label"]], float(h["choice"])))
            except ValueError: pass
        g = rec["target_game"]
        scored = []
        for vk in vectors:
            if (vk, g) not in med: continue
            errs = [abs(v - med[(vk, role)]) / (RANGE[role][1] - RANGE[role][0]) for role, v in obs if (vk, role) in med]
            if len(errs) == len(obs) and errs: scored.append((sum(errs) / len(errs), vk))
        if not scored: continue
        scored.sort(); best = scored[0][0]; ties = [vk for e, vk in scored if e == best]
        pred = statistics.mean(med[(vk, g)] for vk in ties)
        if g == "push_pull": pred = "Push" if pred >= 0.5 else "Pull"
        f.write(json.dumps({"record_idx": i, "user_id": rec["user_id"], "target_game": g, "history_count": len(rec["history"]),
                            "condition": "type_table", "truth": rec["target_answer"], "raw": f"ties={len(ties)}", "prediction": pred}) + "\n"); n += 1
print(f"wrote {n} type-table predictions -> {out}")
