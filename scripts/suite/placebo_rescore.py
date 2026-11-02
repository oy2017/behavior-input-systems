"""Larger rescore of the trait search on fresh people, from stored type tables (no API calls).

DECISION RULE, committed before these results were computed:
- People: records 1000-5999 of data/suite_train/<dataset>.jsonl, none of whom were used in the trait search.
- Two-fold cross-fitting by even/odd index. On each fold, the best subset per pool (over all subset sizes) and each
  item's most common answer come from the OTHER fold, so every person is scored out of sample.
- Primary comparisons: each real pool minus placebo, and each real pool minus the most common answer, on NPAS and
  RIASEC: 8 tests, Holm-corrected at 0.05, using a paired bootstrap over people.
- Supported on a dataset only if a real pool beats BOTH placebo and the most common answer after Holm.
- Sensitivity, not part of the rule: bootstrap over target items, because questions are also a sample.
- The earlier pilot people (records 0-999) are not used, except for a reproduction check.
"""
from __future__ import annotations
import collections, json, statistics
from pathlib import Path
import numpy as np

rng = np.random.default_rng(0)
POOLS = {"npas": ["placebo", "bigfive", "proposed"], "riasec": ["placebo", "bigfive", "holland"]}

def load_table(ds, pool, subset):
    tag = "+".join(t.split(" (")[0].replace(" ", "_") for t in subset)
    draws = collections.defaultdict(list)
    for l in open(f"outputs/type_table/search/{ds}/{pool}__{tag}__L3_d3.jsonl"):
        d = json.loads(l)
        if d["choice"] is not None:
            draws[(json.dumps(d["type_vector"], sort_keys=True), d["item"])].append(d["choice"])
    return draws

def predict(draws, items, ans, tgt, lo, hi):
    """Paper's rule: mean absolute distance to all draws over the person's other items; ties averaged; median draw."""
    vectors = sorted({k[0] for k in draws}); V, I = len(vectors), len(items); vals = np.arange(lo, hi + 1)
    D = np.full((V, I, len(vals)), np.nan); med = np.full((V, I), np.nan)
    for (vk, it), ds in draws.items():
        if it not in items: continue
        v, i = vectors.index(vk), items[it]; arr = np.array(ds, float)
        D[v, i] = np.abs(arr[None, :] - vals[:, None]).mean(1) / max(1, hi - lo); med[v, i] = statistics.median(ds)
    N = len(ans); rows = np.arange(N); e = np.zeros((V, N))
    for v in range(V):
        d = D[v, np.arange(I)[None, :], ans - lo].copy()   # N x I
        d[rows, tgt] = np.nan
        e[v] = np.nanmean(d, axis=1)
    best = np.nanmin(e, axis=0); tied = e <= best + 1e-12
    m = med[:, tgt].copy(); m[~tied] = np.nan
    return np.round(np.nanmean(m, axis=0)).astype(int)

def prepare(recs):
    items = {k: i for i, k in enumerate(sorted({k for r in recs for k in r["items"]}))}
    ans = np.array([[r["items"][k]["answer"] for k in items] for r in recs])
    tgt = np.array([items[r["target_item"]] for r in recs]); truth = ans[np.arange(len(recs)), tgt]
    return items, ans, tgt, truth

def boot(x, groups=None, n=10000):
    if groups is None:
        idx = rng.integers(0, len(x), (n, len(x))); b = x[idx].mean(1)
    else:
        u = np.unique(groups); sums = np.array([x[groups == g].sum() for g in u]); cnts = np.array([(groups == g).sum() for g in u])
        idx = rng.integers(0, len(u), (n, len(u))); b = sums[idx].sum(1) / cnts[idx].sum(1)
    return 100 * x.mean(), 100 * np.percentile(b, 2.5), 100 * np.percentile(b, 97.5), min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))

# ---- reproduction check on the pilot's reporting half
print("Reproduction check, pilot reporting half (expected: riasec bigfive pair 37.0, placebo trio 29.2; npas bigfive pair 39.0)")
for ds, pool, sub in [("riasec", "bigfive", ["Openness", "Extraversion"]), ("riasec", "placebo", ["Preference for the color orange", "Amount of milk in coffee", "Interest in cloud shapes"]), ("npas", "bigfive", ["Openness", "Neuroticism"])]:
    recs = [json.loads(l) for l in open(f"data/suite/{ds}.jsonl")]; items, ans, tgt, truth = prepare(recs)
    sc = recs[0]["scale"]; p = predict(load_table(ds, pool, sub), items, ans, tgt, sc["min"], sc["max"])
    odd = np.arange(len(recs)) % 2 == 1; print(f"  {ds} {pool} {sub}: {100*(p[odd]==truth[odd]).mean():.1f}")

# ---- rescore
results, tests = {}, []
for ds, pools in POOLS.items():
    suite = {json.loads(l)["subject_id"] for l in open(f"data/suite/{ds}.jsonl")}
    recs = [json.loads(l) for l in open(f"data/suite_train/{ds}.jsonl")][1000:]
    assert not any(r["subject_id"] in suite for r in recs), "overlap with pilot people"
    items, ans, tgt, truth = prepare(recs); sc = recs[0]["scale"]; lo, hi = sc["min"], sc["max"]
    fold = np.arange(len(recs)) % 2
    mode_hit = np.zeros(len(recs))   # most common answer from the other fold
    for f in (0, 1):
        tr = fold != f
        for it in range(len(items)):
            # every person answered every item, so use all other-fold answers, not only those whose target this is
            vals, cnts = np.unique(ans[tr, it], return_counts=True); mode = vals[cnts.argmax()]
            te = (fold == f) & (tgt == it); mode_hit[te] = truth[te] == mode
    hits, picks = {}, {}
    for pool in pools:
        S = json.load(open(f"outputs/suite/{ds}/trait_search_{pool}.json"))
        H = {tuple(r["subset"]): (predict(load_table(ds, pool, r["subset"]), items, ans, tgt, lo, hi) == truth).astype(float) for r in S["all_subsets"]}
        h = np.zeros(len(recs)); picked = []
        for f in (0, 1):
            best = max(H, key=lambda k: H[k][fold != f].mean()); h[fold == f] = H[best][fold == f]; picked.append([t.split(" (")[0] for t in best])
        hits[pool], picks[pool] = h, picked
        by = {k: H[k].mean() for k in H}
        results[(ds, pool)] = {"n_subsets": len(H), "best_any": max(by.values()), "worst_any": min(by.values())}
        results[(ds, pool, "sizes")] = {s: 100 * np.mean([v for k, v in by.items() if len(k) == s]) for s in (1, 2, 3)}
        if ("Extraversion", "Agreeableness", "Neuroticism") in H: results[(ds, "borrowed")] = 100 * H[("Extraversion", "Agreeableness", "Neuroticism")].mean()
    print(f"\n## {ds}: n={len(recs)}; most common answer {100*mode_hit.mean():.1f}%" + (f"; borrowed E+A+N trio {results[(ds,'borrowed')]:.1f}%" if (ds, 'borrowed') in results else ""))
    for pool in pools:
        print(f"  {pool:9s} cross-fit {100*hits[pool].mean():5.1f}% | picked {picks[pool][0]} and {picks[pool][1]} | mean by size {[round(float(results[(ds,pool,'sizes')][s]),1) for s in (1,2,3)]} | range of all subsets {100*results[(ds,pool)]['worst_any']:.1f} to {100*results[(ds,pool)]['best_any']:.1f}")
    print(f"  placebo minus most common answer: {'%+.1f (%+.1f, %+.1f) p=%.4f' % boot(hits['placebo'] - mode_hit)}")
    for pool in pools[1:]:
        for name, base in (("placebo", hits["placebo"]), ("most common answer", mode_hit)):
            d = hits[pool] - base; est, a, b, p = boot(d); _, a2, b2, _ = boot(d, groups=tgt)
            tests.append([ds, pool, name, est, a, b, p, a2, b2])
# ---- Holm over the 8 primary tests
order = sorted(range(len(tests)), key=lambda i: tests[i][6]); m = len(tests); adj = [0.0] * m; run = 0.0
for rank, i in enumerate(order):
    run = max(run, min(1.0, (m - rank) * tests[i][6])); adj[i] = run
print("\n| Dataset | Pool | Minus | Gain, points | 95% CI over people | Holm p | 95% CI over items |\n|---|---|---|---|---|---|---|")
for t, a in zip(tests, adj):
    print(f"| {t[0]} | {t[1]} | {t[2]} | {t[3]:+.1f} | {t[4]:+.1f} to {t[5]:+.1f} | {a:.4f} | {t[7]:+.1f} to {t[8]:+.1f} |")
print("\nRule outcome:")
for ds, pools in POOLS.items():
    for pool in pools[1:]:
        ps = [a for t, a in zip(tests, adj) if t[0] == ds and t[1] == pool]; es = [t[3] for t in tests if t[0] == ds and t[1] == pool]
        print(f"  {ds} {pool}: {'SUPPORTED' if all(p < .05 for p in ps) and all(e > 0 for e in es) else 'not supported'}")
