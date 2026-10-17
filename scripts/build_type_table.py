"""Build the (Risk Aversion, Strategic Sophistication, Trust) type table for one model.

125 vectors x 9 game roles x N samples -> outputs/type_table/<model>.jsonl
Resumable: the provider cache skips completed calls.
"""
from __future__ import annotations
import argparse, itertools, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.provider import GeminiClient
from input_systems.conditions import type_vector, TYPE_VECTOR_TRAITS
from input_systems.games import canonical_prompts, parse_answer, GAME_SYSTEM, ROLES

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--samples", type=int, default=10)
ap.add_argument("--workers", type=int, default=8); ap.add_argument("--roles", nargs="*", default=ROLES)
a = ap.parse_args()
prompts = canonical_prompts(Path("data/track_b_subjects.jsonl"))
client = GeminiClient(a.model, workers=a.workers)
out = Path(f"outputs/type_table/{a.model}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
vectors = [dict(zip(TYPE_VECTOR_TRAITS, v)) for v in itertools.product(range(1, 6), repeat=3)]
jobs = [(tv, role, s) for tv in vectors for role in a.roles for s in range(a.samples)]
print(f"{len(jobs)} calls ({len(vectors)} vectors x {len(a.roles)} roles x {a.samples} samples)", flush=True)
t0 = time.time(); done = 0
def run(job):
    tv, role, s = job
    system = GAME_SYSTEM + "\n\n" + type_vector({"type_vector": tv})
    text = client.complete(system, prompts[role], sample=s)
    return {"type_vector": tv, "role": role, "sample": s, "raw": text, "choice": parse_answer(text, role)}
with open(out, "w") as f:
    for i in range(0, len(jobs), 500):
        for rec in client.map(jobs[i:i + 500], run):
            f.write(json.dumps(rec) + "\n")
        done = min(i + 500, len(jobs))
        print(f"{done}/{len(jobs)} done, {client.calls} new API calls, {time.time()-t0:.0f}s", flush=True)
print("finished", out)
