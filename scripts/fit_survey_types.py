"""Fit one survey-side type per Track A record on its 49 other answers (target item never used), then:
  - write fits:  outputs/track_a/<model>/fits_<traits>.jsonl  {record_idx, type_vector, fit_error, ties}
  - write the table-lookup pseudo-condition: outputs/track_a/<model>/type_table_<traits>.jsonl (median over tied types)"""
from __future__ import annotations
import argparse, collections, json, statistics
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--traits", required=True); a = ap.parse_args()
table = collections.defaultdict(list)
for l in Path(f"outputs/type_table/survey_{a.traits}_{a.model}.jsonl").read_text().splitlines():
    d = json.loads(l)
    if d["choice"] is not None: table[(json.dumps(d["type_vector"], sort_keys=True), d["item"])].append(d["choice"])
med = {k: statistics.median(v) for k, v in table.items()}; vectors = sorted({k[0] for k in med})
recs = [json.loads(l) for l in Path("data/track_a_subjects.jsonl").read_text().splitlines()]
d = Path(f"outputs/track_a/{a.model}"); d.mkdir(parents=True, exist_ok=True)
ff = open(d / f"fits_{a.traits}.jsonl", "w"); tf = open(d / f"type_table_{a.traits}.jsonl", "w")
for i, rec in enumerate(recs):
    tgt = rec["target_item"]; obs = [(c, v) for c, v in rec["answers"].items() if c != tgt]
    scored = sorted((sum(abs(v - med[(vk, c)]) for c, v in obs) / (4 * len(obs)), vk) for vk in vectors)
    best = scored[0][0]; ties = [vk for e, vk in scored if e == best]
    ff.write(json.dumps({"record_idx": i, "type_vector": json.loads(ties[0]), "fit_error": best, "ties": len(ties)}) + "\n")
    pred = int(round(statistics.mean(med[(vk, tgt)] for vk in ties)))
    tf.write(json.dumps({"record_idx": i, "subject_id": rec.get("raw_row"), "target_item": tgt, "condition": f"type_table_{a.traits}",
                         "truth": rec["target_answer"], "raw": f"ties={len(ties)}", "prediction": pred}) + "\n")
print(f"fitted {len(recs)} records; mean fit error {statistics.mean(json.loads(l)['fit_error'] for l in open(d / f'fits_{a.traits}.jsonl')):.3f}")
