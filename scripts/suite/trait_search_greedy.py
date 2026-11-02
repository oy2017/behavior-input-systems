"""Greedy per-survey trait search with correct per-item answer scales, for surveys beyond the two-dataset pilot.

DECISION RULE, committed before any result on these six surveys was computed:
- Datasets: mach, dass, fti, nis, gss2022, wvs7. Pools: bigfive and placebo. 3 levels, 3 draws per type and item.
- People: records 1000 onward of data/suite_train/<dataset>.jsonl, not used in the main study.
- Greedy path: best single trait, then the best pair containing it, then the best trio containing that pair, each step
  and the final size chosen on half A (even index). All accuracy reported is on half B (odd index), which played no
  part in selection. The most common answer per item comes from all half A answers to that item.
- Primary tests on half B: bigfive minus placebo, and bigfive minus most common answer, per dataset: 12 tests,
  Holm-corrected at 0.05, paired bootstrap over people.
- A dataset counts as supporting the claim only if bigfive beats both after Holm. Report the count out of six, including
  failures. Sensitivity, not part of the rule: bootstrap over target items.
- Greedy is not exhaustive, so it may miss the best set; the comparison on npas and riasec is a check of that.
Each item's prompt and valid range come from a record whose target is that item, which fixes the wrong-scale bug in
scripts/suite/build_suite_type_table.py on datasets with per-item scales (gss2022, wvs7)."""
from __future__ import annotations
import argparse, collections, json, statistics, sys, time, warnings
from itertools import product
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.suite import item_prompt, type_text, parse_int
warnings.filterwarnings("ignore", category=RuntimeWarning)
POOLS = {"placebo": ["Preference for the color orange", "Amount of milk in coffee", "Interest in cloud shapes", "Enjoyment of the sound of rain", "Fondness for the smell of old books"],
         "bigfive": ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]}
LEVELS, DRAWS = 3, 3

def load(ds):
    suite = [json.loads(l) for l in open(f"data/suite/{ds}.jsonl")]; ids = {r["subject_id"] for r in suite}
    train = [json.loads(l) for l in open(f"data/suite_train/{ds}.jsonl")]
    people = [r for r in train[1000:] if r["subject_id"] not in ids]
    rep = {}
    for r in suite + train: rep.setdefault(r["target_item"], r)
    keys = sorted({k for r in people for k in r["items"]})
    missing = [k for k in keys if k not in rep]; assert not missing, f"no scale for items {missing}"
    return people, rep, {k: i for i, k in enumerate(keys)}

def table(ds, pool, subset, rep, client):
    tag = "+".join(t.replace(" ", "_") for t in subset)
    path = Path(f"outputs/type_table/search/{ds}/{pool}__{tag}__L{LEVELS}_d{DRAWS}.jsonl"); path.parent.mkdir(parents=True, exist_ok=True)
    vectors = [dict(zip(subset, v)) for v in product(range(1, LEVELS + 1), repeat=len(subset))]
    need = len(vectors) * len(rep) * DRAWS
    if path.exists() and sum(1 for _ in open(path)) >= need:
        rows = [json.loads(l) for l in open(path)]
    else:
        jobs = [(tv, k, s) for tv in vectors for k in rep for s in range(DRAWS)]
        def run(job):
            tv, k, s = job; r = rep[k]; sc = r["scale"]
            text = client.complete(r["base_system"] + "\n\n" + type_text(tv, LEVELS), item_prompt(r, k), sample=s)
            return {"type_vector": tv, "item": k, "sample": s, "choice": parse_int(text, sc["min"], sc["max"])}
        rows = []
        for i in range(0, len(jobs), 2000): rows += client.map(jobs[i:i + 2000], run)
        with open(path, "w") as f:
            for d in rows: f.write(json.dumps(d) + "\n")
    draws = collections.defaultdict(list)
    for d in rows:
        if d["choice"] is not None: draws[(json.dumps(d["type_vector"], sort_keys=True), d["item"])].append(d["choice"])
    return draws

def arrays(people, idx):
    ans = np.full((len(people), len(idx)), -1, int)
    for n, r in enumerate(people):
        for k, v in r["items"].items(): ans[n, idx[k]] = v["answer"]
    tgt = np.array([idx[r["target_item"]] for r in people])
    return ans, tgt, ans[np.arange(len(people)), tgt]

def predict(draws, idx, rep, ans, tgt):
    """Paper's rule: mean distance to all draws, normalised per item; ties averaged; median draw of the type."""
    vectors = sorted({k[0] for k in draws}); V, I = len(vectors), len(idx)
    glo = min(rep[k]["scale"]["min"] for k in idx); ghi = max(rep[k]["scale"]["max"] for k in idx); vals = np.arange(glo, ghi + 1)
    D = np.full((V, I, len(vals)), np.nan); med = np.full((V, I), np.nan); vpos = {v: i for i, v in enumerate(vectors)}
    for (vk, it), ds in draws.items():
        if it not in idx: continue
        sc = rep[it]["scale"]; arr = np.array(ds, float)
        D[vpos[vk], idx[it]] = np.abs(arr[None, :] - vals[:, None]).mean(1) / max(1, sc["max"] - sc["min"]); med[vpos[vk], idx[it]] = statistics.median(ds)
    N = len(ans); rows = np.arange(N); e = np.zeros((V, N)); col = np.arange(I)[None, :]; a = np.clip(ans - glo, 0, len(vals) - 1)
    for v in range(V):
        d = D[v, col, a].copy(); d[ans < 0] = np.nan; d[rows, tgt] = np.nan; e[v] = np.nanmean(d, axis=1)
    best = np.nanmin(e, axis=0); tied = e <= best + 1e-12
    m = med[:, tgt].copy(); m[~tied] = np.nan
    return np.round(np.nanmean(m, axis=0))

def search(ds, pool, client):
    people, rep, idx = load(ds); ans, tgt, truth = arrays(people, idx); A = np.arange(len(people)) % 2 == 0; B = ~A
    traits = POOLS[pool]; path = []; current = (); t0 = time.time()
    for size in (1, 2, 3):
        cands = [tuple(sorted(current + (t,), key=traits.index)) for t in traits if t not in current]; scored = []
        for c in cands:
            hit = predict(table(ds, pool, c, rep, client), idx, rep, ans, tgt) == truth
            scored.append((hit[A].mean(), hit[B].mean(), c))
            print(f"[{ds}/{pool} size {size}] {'+'.join(c):95s} A={hit[A].mean():.3f} ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)
        accA, accB, current = max(scored, key=lambda x: x[0]); path.append({"size": size, "subset": list(current), "accA": float(accA), "accB_hidden_until_analysis": float(accB), "candidates": [[list(c), float(a)] for a, b, c in scored]})
    Path(f"outputs/suite/{ds}").mkdir(parents=True, exist_ok=True); Path(f"outputs/suite/{ds}/greedy_{pool}.json").write_text(json.dumps(path, indent=1))
    print(f"finished {ds} {pool}", flush=True)

def boot(x, rng, groups=None, n=10000):
    if groups is None: b = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    else:
        u = np.unique(groups); s = np.array([x[groups == g].sum() for g in u]); c = np.array([(groups == g).sum() for g in u]); i = rng.integers(0, len(u), (n, len(u))); b = s[i].sum(1) / c[i].sum(1)
    return 100 * x.mean(), 100 * np.percentile(b, 2.5), 100 * np.percentile(b, 97.5), min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))

def analyze(datasets):
    rng = np.random.default_rng(0); tests = []; lines = []
    for ds in datasets:
        people, rep, idx = load(ds); ans, tgt, truth = arrays(people, idx); A = np.arange(len(people)) % 2 == 0; B = ~A
        mode = {}
        for it, i in idx.items():
            v = ans[A, i]; v = v[v >= 0]; u, c = np.unique(v, return_counts=True); mode[i] = u[c.argmax()]
        m = np.array([truth[n] == mode[tgt[n]] for n in range(len(people))], float); H = {}; picks = {}
        for pool in ("placebo", "bigfive"):
            path = json.load(open(f"outputs/suite/{ds}/greedy_{pool}.json")); best = max(path, key=lambda s: s["accA"])
            H[pool] = (predict(table(ds, pool, tuple(best["subset"]), rep, None), idx, rep, ans, tgt) == truth).astype(float)[B]; picks[pool] = best["subset"]
        lines.append(f"{ds}: n={B.sum()} most common answer {100*m[B].mean():.1f} | placebo {100*H['placebo'].mean():.1f} {picks['placebo']} | bigfive {100*H['bigfive'].mean():.1f} {picks['bigfive']}")
        for name, base in (("placebo", H["placebo"]), ("most common answer", m[B])):
            d = H["bigfive"] - base; e, a, b, p = boot(d, rng); _, a2, b2, _ = boot(d, rng, groups=tgt[B]); tests.append([ds, name, e, a, b, p, a2, b2])
    order = sorted(range(len(tests)), key=lambda i: tests[i][5]); adj = [0.0] * len(tests); run = 0.0
    for r, i in enumerate(order): run = max(run, min(1.0, (len(tests) - r) * tests[i][5])); adj[i] = run
    print("\n".join(lines)); print("\n| Dataset | Big Five minus | Gain | 95% CI over people | Holm p | 95% CI over items |\n|---|---|---|---|---|---|")
    for t, a in zip(tests, adj): print(f"| {t[0]} | {t[1]} | {t[2]:+.1f} | {t[3]:+.1f} to {t[4]:+.1f} | {a:.4f} | {t[6]:+.1f} to {t[7]:+.1f} |")
    print("\nRule outcome:"); n = 0
    for ds in datasets:
        ok = all(a < .05 and t[2] > 0 for t, a in zip(tests, adj) if t[0] == ds); n += ok; print(f"  {ds}: {'SUPPORTED' if ok else 'not supported'}")
    print(f"Supported on {n} of {len(datasets)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset"); ap.add_argument("--pool"); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--analyze", nargs="*"); a = ap.parse_args()
    if a.analyze is not None: analyze(a.analyze)
    else:
        from input_systems.provider import GeminiClient
        search(a.dataset, a.pool, GeminiClient("gemini-3.5-flash", workers=a.workers))
