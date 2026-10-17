"""Track B main run: conditions x all Across-Ctx records -> outputs/track_b/<model>/<condition>.jsonl

Conditions available now: none, history. type_vector and history+type_vector need the type table
and a fitted vector per record (added by scripts/fit_type_vectors.py).
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.provider import GeminiClient
from input_systems.conditions import type_vector
from input_systems.games import target_instruction, parse_answer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--conditions", nargs="+", default=["none", "history"])
ap.add_argument("--workers", type=int, default=8); ap.add_argument("--limit", type=int, default=None)
ap.add_argument("--fits", type=Path, default=None, help="jsonl of {record_idx, type_vector} from fit_type_vectors.py")
ap.add_argument("--draws", type=int, default=1, help="draws per record; >1 writes <cond>_x<draws>.jsonl with all predictions")
a = ap.parse_args()
recs = [json.loads(l) for l in Path("data/track_b_subjects.jsonl").read_text().splitlines()][: a.limit]
fits = {}
if a.fits and a.fits.exists():
    fits = {d["record_idx"]: d["type_vector"] for d in map(json.loads, a.fits.read_text().splitlines())}
client = GeminiClient(a.model, workers=a.workers)

def build(rec, cond, idx):
    r = rec["record"]; system = r["system"]; user = r["user"]
    if cond in ("none", "type_vector"):
        user = target_instruction(user)
    if cond in ("type_vector", "history+type_vector"):
        system = system + "\n\n" + type_vector({"type_vector": fits[idx]})
    return system, user

for cond in a.conditions:
    out = Path(f"outputs/track_b/{a.model}/{cond}{'_x%d' % a.draws if a.draws > 1 else ''}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
    jobs = [(i, rec) for i, rec in enumerate(recs) if "type_vector" not in cond or i in fits]
    t0 = time.time(); print(f"[{cond}] {len(jobs)} records", flush=True)
    def run(job):
        i, rec = job; system, user = build(rec, cond, i)
        # draw k uses sample index i for k=0 (shares the cache with the single-draw run) and 10_000*k + i otherwise
        texts = [client.complete(system, user, sample=(i if k == 0 else 10_000 * k + i)) for k in range(a.draws)]
        preds = [parse_answer(t, rec["target_game"]) for t in texts]
        d = {"record_idx": i, "user_id": rec["user_id"], "target_game": rec["target_game"],
             "history_count": len(rec["history"]), "condition": cond, "truth": rec["target_answer"],
             "raw": texts[0], "prediction": preds[0]}
        if a.draws > 1: d["predictions"] = preds
        return d
    with open(out, "w") as f:
        for s in range(0, len(jobs), 500):
            for d in client.map(jobs[s:s + 500], run):
                f.write(json.dumps(d) + "\n")
            print(f"[{cond}] {min(s+500, len(jobs))}/{len(jobs)}, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
    print("finished", out, flush=True)
