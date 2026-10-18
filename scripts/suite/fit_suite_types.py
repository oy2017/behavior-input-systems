"""Fit (E,A,N) type per record from history items via the dataset's type table; write fits + type_table pseudo-condition."""
from __future__ import annotations
import argparse, collections, json, statistics
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--model", default="gemini-3.5-flash"); a = ap.parse_args()
table = collections.defaultdict(list)
for l in Path(f"outputs/type_table/suite_{a.dataset}_{a.model}.jsonl").read_text().splitlines():
    d = json.loads(l)
    if d["choice"] is not None: table[(json.dumps(d["type_vector"], sort_keys=True), d["item_text"])].append(d["choice"])
med = {k: statistics.median(v) for k, v in table.items()}; vectors = sorted({k[0] for k in med})
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()]
d = Path(f"outputs/suite/{a.dataset}/{a.model}"); d.mkdir(parents=True, exist_ok=True)
ff = open(d / "fits.jsonl", "w"); tf = open(d / "type_table.jsonl", "w"); nf = 0
for i, r in enumerate(recs):
    tgt = r["target_item"]; sc = r["scale"]; rng = max(1, sc["max"] - sc["min"])
    obs = [(v["text"], v["answer"]) for k, v in r["items"].items() if k != tgt and any((vk, v["text"]) in med for vk in vectors[:1])]
    scored = []
    for vk in vectors:
        errs = [abs(ans - med[(vk, t)]) / rng for t, ans in obs if (vk, t) in med]
        if errs: scored.append((sum(errs) / len(errs), vk))
    if not scored: continue
    scored.sort(); best = scored[0][0]; ties = [vk for e, vk in scored if e == best]
    ttext = r["items"][tgt]["text"]; ties_t = [vk for vk in ties if (vk, ttext) in med]
    if not ties_t: continue
    ff.write(json.dumps({"record_idx": i, "type_vector": json.loads(ties[0]), "fit_error": best, "ties": len(ties), "n_history": len(obs)}) + "\n")
    pred = int(round(statistics.mean(med[(vk, ttext)] for vk in ties_t)))
    tf.write(json.dumps({"record_idx": i, "subject_id": r["subject_id"], "target_item": tgt, "condition": "type_table", "truth": r["items"][tgt]["answer"],
                         "lo": sc["min"], "hi": sc["max"], "raw": f"ties={len(ties)}", "prediction": pred}) + "\n"); nf += 1
print(f"{a.dataset}: fitted {nf}/{len(recs)}")
