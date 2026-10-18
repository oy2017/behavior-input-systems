"""Type table for a suite dataset: 27 (E,A,N) vectors x all items x N samples -> outputs/type_table/suite_<dataset>_<model>.jsonl"""
from __future__ import annotations
import argparse, itertools, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.provider import GeminiClient
from input_systems.suite import TRAITS_BF3, item_prompt, type_text, parse_int

ap = argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--samples", type=int, default=5); ap.add_argument("--workers", type=int, default=8); a = ap.parse_args()
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()]
# item universe: union over records (GSS/SocSci have per-record items); keep one representative record per item for its prompt/scale
items = {}
for r in recs:
    for k in r["items"]:
        items.setdefault((k, r["items"][k]["text"]), r)
if len(items) > 120:  # SocSci210 has thousands of distinct stimuli; restrict the table to target items only
    items = {(r["target_item"], r["items"][r["target_item"]]["text"]): r for r in recs}
vectors = [dict(zip(TRAITS_BF3, v)) for v in itertools.product(range(1, 4), repeat=3)]
jobs = [(tv, key, r, s) for tv in vectors for key, r in items.items() for s in range(a.samples)]
client = GeminiClient(a.model, workers=a.workers)
out = Path(f"outputs/type_table/suite_{a.dataset}_{a.model}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
print(f"{a.dataset}: {len(jobs)} calls ({len(vectors)} vectors x {len(items)} items x {a.samples})", flush=True); t0 = time.time()
def run(job):
    tv, (k, text), r, s = job; sc = r["scale"]
    resp = client.complete(r["base_system"] + "\n\n" + type_text(tv), item_prompt(r, k), sample=s)
    return {"type_vector": tv, "item": k, "item_text": text, "sample": s, "raw": resp, "choice": parse_int(resp, sc["min"], sc["max"]), "lo": sc["min"], "hi": sc["max"]}
with open(out, "w") as f:
    for i in range(0, len(jobs), 500):
        for d in client.map(jobs[i:i + 500], run): f.write(json.dumps(d) + "\n")
        print(f"{min(i+500, len(jobs))}/{len(jobs)} done, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
print("finished", out, flush=True)
