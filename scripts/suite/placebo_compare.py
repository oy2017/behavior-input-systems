"""Paired comparison on held-out people of trait sets chosen by trait_search.py, from stored tables (no API calls).
Rebuilds per-person type-based predictions for the subsets chosen on half A, then scores half B. Compares each real
pool with the placebo pool at each size and at the best size chosen on half A, and each with the most common answer.
Intervals: paired record bootstrap, 10,000 resamples."""
from __future__ import annotations
import collections, json, statistics
from pathlib import Path
import numpy as np
rng = np.random.default_rng(0)
POOLS = {"npas": ["placebo", "bigfive", "proposed"], "riasec": ["placebo", "bigfive", "holland"]}

def preds(ds, pool, subset, recs):
    tag = "+".join(t.split(" (")[0].replace(" ", "_") for t in subset)
    draws = collections.defaultdict(list)
    for l in open(f"outputs/type_table/search/{ds}/{pool}__{tag}__L3_d3.jsonl"):
        d = json.loads(l)
        if d["choice"] is not None: draws[(json.dumps(d["type_vector"], sort_keys=True), d["item"])].append(d["choice"])
    vectors = sorted({k[0] for k in draws}); out = {}
    arr = {k: np.array(v, float) for k, v in draws.items()}
    for i, r in enumerate(recs):
        tgt = r["target_item"]; rg = max(1, r["scale"]["max"] - r["scale"]["min"])
        hist = [(k, v["answer"]) for k, v in r["items"].items() if k != tgt]
        scored = [(float(np.mean([np.mean(np.abs(arr[(vk, k)] - a)) / rg for k, a in hist if (vk, k) in arr])), vk) for vk in vectors]
        scored.sort(); best = scored[0][0]; ties = [vk for e, vk in scored if e == best and (vk, tgt) in arr]
        if ties: out[i] = int(round(float(np.mean([statistics.median(draws[(vk, tgt)]) for vk in ties]))))
    return out

def ci(x):
    idx = rng.integers(0, len(x), (10000, len(x))); b = x[idx].mean(1) * 100
    return f"{100*x.mean():+.1f} ({np.percentile(b,2.5):+.1f}, {np.percentile(b,97.5):+.1f})"

for ds, pools in POOLS.items():
    recs = [json.loads(l) for l in open(f"data/suite/{ds}.jsonl")]
    B = [i for i in range(len(recs)) if i % 2 == 1]
    truth = {i: recs[i]["items"][recs[i]["target_item"]]["answer"] for i in B}
    BR = json.load(open(f"data/suite_baserates/{ds}.json"))["items"]
    mode = {i: int(max(BR[recs[i]["target_item"]]["pop"], key=BR[recs[i]["target_item"]]["pop"].get)) for i in B}
    hits = {}; chosen = {}
    for pool in pools:
        S = json.load(open(f"outputs/suite/{ds}/trait_search_{pool}.json"))
        for k, v in S["per_size"].items():
            p = preds(ds, pool, v["chosen_on_A"], recs)
            hits[(pool, k)] = np.array([p.get(i) == truth[i] for i in B], float); chosen[(pool, k)] = (v["chosen_on_A"], v["accA"])
        chosen[(pool, "best")] = max(((chosen[(pool, k)][1], k) for k in S["per_size"]))
    m = np.array([mode[i] == truth[i] for i in B], float)
    print(f"\n## {ds}: n={len(B)}, most common answer {100*m.mean():.1f}%")
    print("| pool | traits | held-out % | minus placebo, same size (95% CI) | minus most common answer (95% CI) |\n|---|---|---|---|---|")
    for pool in pools:
        for k in ["1", "2", "3"]:
            h = hits[(pool, k)]; dp = "-" if pool == "placebo" else ci(h - hits[("placebo", k)])
            print(f"| {pool} | {k} | {100*h.mean():.1f} | {dp} | {ci(h - m)} |")
    pb = hits[("placebo", chosen[("placebo", "best")][1])]
    print("Best size chosen on half A, against the placebo's best size:")
    for pool in pools[1:]:
        k = chosen[(pool, "best")][1]; print(f"  {pool} size {k}: {100*hits[(pool,k)].mean():.1f} vs placebo size {chosen[('placebo','best')][1]}: {100*pb.mean():.1f} | diff {ci(hits[(pool,k)] - pb)}")
