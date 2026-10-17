"""Survey-side type table: for each type vector over a trait set (3-level Likert, as in Jackson et al.'s
trait-set comparison) and each of the 50 Big Five items, sample the model's answer N times.
Output: outputs/type_table/survey_<traits>_<model>.jsonl"""
from __future__ import annotations
import argparse, itertools, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.provider import GeminiClient
from input_systems.subjects import load_codebook, COLS

TRAIT_SETS = {"econ": ["Risk Aversion", "Strategic Sophistication", "Trust"],
              "bigfive": ["Extraversion", "Agreeableness", "Neuroticism"]}
ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini-3.5-flash"); ap.add_argument("--traits", choices=TRAIT_SETS, required=True)
ap.add_argument("--levels", type=int, default=3); ap.add_argument("--samples", type=int, default=10); ap.add_argument("--workers", type=int, default=8)
a = ap.parse_args()
traits = TRAIT_SETS[a.traits]
code = load_codebook(Path("data/big5_raw/BIG5/codebook.txt")); item_text = {v: k for k, v in code.items()}
ITEM = ("The following item was rated on a five-point scale where 1=Disagree, 2=Partially Disagree, 3=Neutral, "
        "4=Partially Agree, 5=Agree. Please select how this statement describes you and highlight your answer in []"
        "(such as [1],[2],[3],[4],or [5]): {item} Only output your answer in brackets.")
def cap(s): return s[0].upper() + s[1:]
def sysprompt(tv):
    return ("You are a person answering a personality survey.\n\n"
            f"You are characterized by the following profile (each dimension is measured on a Likert scale, where 1 is the lowest level and {a.levels} is the highest).\n"
            + "\n".join(f"- {t}: {tv[t]} out of {a.levels}" for t in traits))
vectors = [dict(zip(traits, v)) for v in itertools.product(range(1, a.levels + 1), repeat=len(traits))]
jobs = [(tv, c, s) for tv in vectors for c in COLS for s in range(a.samples)]
client = GeminiClient(a.model, workers=a.workers)
out = Path(f"outputs/type_table/survey_{a.traits}_{a.model}.jsonl")
print(f"{len(jobs)} calls ({len(vectors)} vectors x 50 items x {a.samples})", flush=True); t0 = time.time()
def run(job):
    tv, c, s = job
    text = client.complete(sysprompt(tv), ITEM.format(item=cap(item_text[c])), sample=s)
    m = re.findall(r"\[([1-5])\]", text)
    return {"type_vector": tv, "item": c, "sample": s, "raw": text, "choice": int(m[-1]) if m else None}
with open(out, "w") as f:
    for i in range(0, len(jobs), 500):
        for rec in client.map(jobs[i:i + 500], run): f.write(json.dumps(rec) + "\n")
        print(f"{min(i+500, len(jobs))}/{len(jobs)} done, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
print("finished", out, flush=True)
