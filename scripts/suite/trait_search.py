"""Per-survey trait search, following Jackson et al. (2026) Sec. 4.2-4.3:
for every candidate subset of a trait pool (sizes --sizes, --levels Likert levels), build the type table
(every type x every item x --draws), fit each person's best-fitting type on their OTHER items using the
paper's rule (mean absolute distance to all draws, normalised by range; ties kept), and predict the held-out
item by type-based prediction (median of the type's draws; ties averaged).
Selection on held-out people: subsets are chosen on half A (even record index) and reported on half B (odd).
Pools: bigfive | holland | proposed (the model names traits for this questionnaire; cached) | custom:A,B,C
Writes outputs/suite/<dataset>/trait_search_<pool>.json and the tables under outputs/type_table/search/."""
from __future__ import annotations
import argparse, collections, itertools, json, re, statistics, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.provider import GeminiClient
from input_systems.suite import item_prompt, type_text, parse_int

POOLS = {"bigfive": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"],
         "holland": ["Realistic (hands-on, practical)", "Investigative (analytical, scientific)", "Artistic (creative, expressive)",
                     "Social (helping, teaching)", "Enterprising (persuading, leading)", "Conventional (organised, detail-oriented)"]}
ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True); ap.add_argument("--pool", required=True); ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--sizes", nargs="+", type=int, default=[1, 2, 3]); ap.add_argument("--levels", type=int, default=3); ap.add_argument("--draws", type=int, default=3)
ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max-subsets", type=int, default=None)
a = ap.parse_args()
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()]
items = {}
for r in recs:
    for k, v in r["items"].items(): items.setdefault(k, (v["text"], r))
client = GeminiClient(a.model, workers=a.workers)
# ---- pool
if a.pool.startswith("custom:"): traits = [t.strip() for t in a.pool[7:].split(",")]
elif a.pool == "proposed":
    cache = Path(f"data/suite_pools/{a.dataset}_proposed.json"); cache.parent.mkdir(exist_ok=True)
    if cache.exists(): traits = json.loads(cache.read_text())
    else:
        listing = "\n".join(f"- {t}" for t, _ in list(items.values())[:60])
        txt = client.complete("You are a psychometrician.",
            "Below are the items of a questionnaire. Name the five personality or disposition traits on which people differ most in how they answer these items. "
            "Each trait must be a short noun phrase (1 to 4 words) that could be rated from 1 (lowest) to 3 (highest). Output exactly five lines, one trait per line, nothing else.\n\n" + listing, sample=0)
        traits = [re.sub(r"^[\-\d\.\)\s]+", "", l).strip() for l in txt.strip().splitlines() if l.strip()][:5]
        cache.write_text(json.dumps(traits))
else: traits = POOLS[a.pool]
print(f"{a.dataset} pool={a.pool}: {traits}", flush=True)
subsets = [c for k in a.sizes for c in itertools.combinations(traits, k)]
if a.max_subsets: subsets = subsets[: a.max_subsets]
print(f"{len(subsets)} subsets; items={len(items)}; levels={a.levels}; draws={a.draws}", flush=True)
# ---- tables
tdir = Path(f"outputs/type_table/search/{a.dataset}"); tdir.mkdir(parents=True, exist_ok=True)
def table_for(subset):
    tag = "+".join(t.split(" (")[0].replace(" ", "_") for t in subset)
    out = tdir / f"{a.pool}__{tag}__L{a.levels}_d{a.draws}.jsonl"
    vectors = [dict(zip(subset, v)) for v in itertools.product(range(1, a.levels + 1), repeat=len(subset))]
    if out.exists() and sum(1 for _ in open(out)) >= len(vectors) * len(items) * a.draws:
        rows = [json.loads(l) for l in open(out)]
    else:
        jobs = [(tv, k, s) for tv in vectors for k in items for s in range(a.draws)]
        def run(job):
            tv, k, s = job; text, r = items[k]; sc = r["scale"]
            resp = client.complete(r["base_system"] + "\n\n" + type_text(tv, a.levels), item_prompt(r, k), sample=s)
            return {"type_vector": tv, "item": k, "sample": s, "choice": parse_int(resp, sc["min"], sc["max"])}
        rows = []
        for i in range(0, len(jobs), 1000): rows += client.map(jobs[i:i + 1000], run)
        with open(out, "w") as f:
            for d in rows: f.write(json.dumps(d) + "\n")
    draws = collections.defaultdict(list)
    for d in rows:
        if d["choice"] is not None: draws[(json.dumps(d["type_vector"], sort_keys=True), d["item"])].append(d["choice"])
    return draws
# ---- fit + predict (paper's rule)
def evaluate(draws, subset):
    vectors = sorted({k[0] for k in draws}); preds = {}
    for i, r in enumerate(recs):
        tgt = r["target_item"]; sc = r["scale"]; rng = max(1, sc["max"] - sc["min"])
        hist = [(k, v["answer"]) for k, v in r["items"].items() if k != tgt]
        scored = []
        for vk in vectors:
            ds = [np.mean(np.abs(np.array(draws[(vk, k)]) - ans)) / rng for k, ans in hist if (vk, k) in draws]
            if ds: scored.append((float(np.mean(ds)), vk))
        if not scored: continue
        scored.sort(); best = scored[0][0]; ties = [vk for e, vk in scored if e == best and (vk, tgt) in draws]
        if not ties: continue
        preds[i] = int(round(float(np.mean([statistics.median(draws[(vk, tgt)]) for vk in ties]))))
    def score(idx):
        ok = [i for i in idx if i in preds]
        if not ok: return {"n": 0}
        t = np.array([recs[i]["items"][recs[i]["target_item"]]["answer"] for i in ok]); p = np.array([preds[i] for i in ok])
        rngs = np.array([max(1, recs[i]["scale"]["max"] - recs[i]["scale"]["min"]) for i in ok])
        return {"n": len(ok), "acc": float(np.mean(t == p)), "nmae": float(np.mean(100 * np.abs(t - p) / rngs))}
    A = [i for i in range(len(recs)) if i % 2 == 0]; B = [i for i in range(len(recs)) if i % 2 == 1]
    return {"subset": list(subset), "halfA": score(A), "halfB": score(B), "all": score(range(len(recs)))}
results = []; t0 = time.time()
for n, subset in enumerate(subsets, 1):
    res = evaluate(table_for(subset), subset); results.append(res)
    print(f"[{n}/{len(subsets)}] {'+'.join(s.split(' (')[0] for s in subset):60s} A={res['halfA'].get('acc', float('nan')):.3f} B={res['halfB'].get('acc', float('nan')):.3f}  ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)
# ---- select on A, report on B, per size
by_size = collections.defaultdict(list)
for r in results: by_size[len(r["subset"])].append(r)
summary = {"dataset": a.dataset, "pool": a.pool, "traits": traits, "levels": a.levels, "draws": a.draws, "per_size": {}}
for k, rs in sorted(by_size.items()):
    best = max(rs, key=lambda r: r["halfA"].get("acc", -1))
    summary["per_size"][k] = {"chosen_on_A": best["subset"], "accA": best["halfA"]["acc"], "reported_accB": best["halfB"]["acc"], "reported_nmaeB": best["halfB"]["nmae"]}
    print(f"size {k}: chosen {best['subset']} -> held-out accuracy {best['halfB']['acc']:.3f}", flush=True)
summary["all_subsets"] = results
Path(f"outputs/suite/{a.dataset}/trait_search_{a.pool}.json").write_text(json.dumps(summary, indent=1))
print("finished", a.dataset, a.pool, flush=True)
