"""Run suite conditions for one dataset -> outputs/suite/<dataset>/<model>/<condition>.jsonl"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.provider import GeminiClient
from input_systems.suite import build_system, item_prompt, parse_int

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True); ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--conditions", nargs="+", default=["none", "demographics", "traits", "history", "demographics+traits", "demographics+history"])
ap.add_argument("--fits", type=Path, default=None); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--limit", type=int, default=None)
a = ap.parse_args()
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()][: a.limit]
fits = {d["record_idx"]: d["type_vector"] for d in map(json.loads, a.fits.read_text().splitlines())} if a.fits else {}
client = GeminiClient(a.model, workers=a.workers)
for cond in a.conditions:
    if "traits" in cond and not recs[0].get("traits"): print(f"[{cond}] skipped: dataset has no traits"); continue
    out = Path(f"outputs/suite/{a.dataset}/{a.model}/{cond}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
    jobs = [(i, r) for i, r in enumerate(recs) if "type_vector" not in cond or i in fits]
    t0 = time.time(); print(f"[{a.dataset}/{cond}] {len(jobs)} records", flush=True)
    def run(job):
        i, r = job; system = build_system(r, cond, fits.get(i)); user = item_prompt(r, r["target_item"])
        text = client.complete(system, user, sample=i); sc = r["scale"]
        return {"record_idx": i, "subject_id": r["subject_id"], "target_item": r["target_item"], "condition": cond,
                "truth": r["items"][r["target_item"]]["answer"], "lo": sc["min"], "hi": sc["max"], "raw": text, "prediction": parse_int(text, sc["min"], sc["max"])}
    with open(out, "w") as f:
        for s in range(0, len(jobs), 500):
            for d in client.map(jobs[s:s + 500], run): f.write(json.dumps(d) + "\n")
            print(f"[{a.dataset}/{cond}] {min(s+500, len(jobs))}/{len(jobs)}, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
    print("finished", out, flush=True)
