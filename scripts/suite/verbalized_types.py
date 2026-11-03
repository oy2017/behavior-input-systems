"""Verbalized learned types: can a written description of a data-learned group carry what the group predicts?

DECISION RULE, committed before any result of this experiment was computed:
- Surveys: npas, riasec, mach, dass, fti, nis, gss2022, wvs7. People: records 1000 onward; half A (even index) is used
  to learn 27 k-means groups (same settings as type_vector_diagnostics.py) and to write descriptions; all scoring is on
  half B.
- Each group is described by Gemini 3.5 Flash (thinking off) from its 12 most distinctive items, in at most 80 words,
  with no numbers and no quoted items. Each description then answers every item 3 times (the "verbal table").
- Main condition, "verbal types": each half B person gets the description whose generated answers best match their
  other answers (the same rule as type vectors), and is predicted with that description's median answer.
- Secondary condition, "verbal types, data assignment": each person gets the description of the group k-means assigns.
- Primary tests on half B: verbal types minus chosen Big Five type vector, and verbal types minus learned types, per
  survey: 16 tests, Holm-corrected at 0.05, paired bootstrap over people.
- Reading fixed in advance: if verbal types beat type vectors on most surveys and come close to learned types, the
  limit of type vectors was the choice of trait words. If verbal types do no better than type vectors, the model cannot
  turn a description of a person into the right answers, whatever the words.
- Descriptions containing digits are reported, not removed."""
from __future__ import annotations
import argparse, json, re, sys, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from trait_search_greedy import load, arrays, table, predict
from input_systems.suite import item_prompt, parse_int
warnings.filterwarnings("ignore")
K, DRAWS = 27, 3

def learned(ds):
    people, rep, idx = load(ds); ans, tgt, truth = arrays(people, idx); A = np.arange(len(people)) % 2 == 0; B = ~A
    I = len(idx); keys = sorted(idx, key=idx.get)
    rngs = np.array([max(1, rep[k]["scale"]["max"] - rep[k]["scale"]["min"]) for k in keys])
    X = ans.astype(float); X[ans < 0] = np.nan; col_mean = np.nanmean(X[A], 0); X = np.where(np.isnan(X), col_mean, X) / rngs
    km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(X[A])
    return people, rep, idx, ans, tgt, truth, A, B, keys, km, X

def describe(ds, client):
    people, rep, idx, ans, tgt, truth, A, B, keys, km, X = learned(ds)
    H = ans[A].astype(float); H[ans[A] < 0] = np.nan; mu = np.nanmean(H, 0); sd = np.nanstd(H, 0) + 1e-9
    out = {}
    for c in range(K):
        mem = H[km.labels_ == c]; m = np.nanmean(mem, 0); z = (m - mu) / sd
        top = np.argsort(-np.abs(np.nan_to_num(z)))[:12]
        lines = []
        for i in top:
            sc = rep[keys[i]]["scale"]; t = rep[keys[i]]["items"][keys[i]]["text"]
            lines.append(f'- "{t}" ({sc["min"]} to {sc["max"]}): this group averages {m[i]:.1f}, everyone averages {mu[i]:.1f}')
        user = (f"Below are the questionnaire items on which one group of respondents ({len(mem)} people, "
                f"{100*len(mem)/A.sum():.0f}% of all) differs most from everyone else.\n\n" + "\n".join(lines) +
                "\n\nWrite a description of a typical person in this group, addressed to them in the second person "
                "(\"You are someone who...\"). Describe their dispositions, values, habits or tendencies. Use 3 to 5 "
                "sentences and at most 80 words. Do not use numbers and do not quote or list the questionnaire items.")
        out[c] = client.complete("You are a psychologist who summarizes groups of survey respondents.", user, sample=0).strip()
    Path(f"outputs/suite/{ds}/verbal_types.json").write_text(json.dumps(out, indent=1))
    return out

def verbal_table(ds, desc, rep, client):
    path = Path(f"outputs/type_table/search/{ds}/verbal__k{K}_d{DRAWS}.jsonl")
    if path.exists() and sum(1 for _ in open(path)) >= K * len(rep) * DRAWS:
        rows = [json.loads(l) for l in open(path)]
    else:
        jobs = [(c, k, s) for c in range(K) for k in rep for s in range(DRAWS)]
        def run(job):
            c, k, s = job; r = rep[k]; sc = r["scale"]
            text = client.complete(r["base_system"] + "\n\n" + desc[str(c)] if isinstance(next(iter(desc)), str) else r["base_system"] + "\n\n" + desc[c], item_prompt(r, k), sample=s)
            return {"cluster": c, "item": k, "sample": s, "choice": parse_int(text, sc["min"], sc["max"])}
        rows = []
        for i in range(0, len(jobs), 2000): rows += client.map(jobs[i:i + 2000], run)
        with open(path, "w") as f:
            for d in rows: f.write(json.dumps(d) + "\n")
    draws = {}
    for d in rows:
        if d["choice"] is not None: draws.setdefault((f"c{d['cluster']:02d}", d["item"]), []).append(d["choice"])
    return draws

def build(ds, client):
    t0 = time.time(); desc = describe(ds, client)
    _, rep, *_ = learned(ds)
    verbal_table(ds, {str(k): v for k, v in desc.items()}, rep, client)
    print(f"finished {ds} ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)

def analyze(datasets):
    rng = np.random.default_rng(0); tests = []; lines = []; digits = 0
    def boot(d):
        b = 100 * d[rng.integers(0, len(d), (10000, len(d)))].mean(1)
        return 100 * d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    for ds in datasets:
        people, rep, idx, ans, tgt, truth, A, B, keys, km, X = learned(ds); I = len(idx)
        desc = json.load(open(f"outputs/suite/{ds}/verbal_types.json")); digits += sum(bool(re.search(r"\d", v)) for v in desc.values())
        draws = verbal_table(ds, desc, rep, None)
        vt = (predict(draws, idx, rep, ans, tgt) == truth)
        # data assignment: k-means cluster from other items, then that description's median
        Bi = np.where(B)[0]; obs = ans >= 0; C = km.cluster_centers_
        lab = np.array([np.nanargmin([np.nanmean(np.where(obs[n] & (np.arange(I) != tgt[n]), (X[n] - C[k]) ** 2, np.nan)) for k in range(K)]) for n in Bi])
        med = {key: np.median(v) for key, v in draws.items()}
        vd = np.array([round(med.get((f"c{lab[j]:02d}", keys[tgt[n]]), np.nan)) == truth[n] if (f"c{lab[j]:02d}", keys[tgt[n]]) in med else False for j, n in enumerate(Bi)], float)
        # references, recomputed on the same people
        mode = {}
        for i in range(I):
            v = ans[A, i]; v = v[v >= 0]; u, c = np.unique(v, return_counts=True); mode[i] = u[c.argmax()]
        m = np.array([truth[n] == mode[tgt[n]] for n in Bi], float)
        Aidx = np.where(A)[0]; lt = []
        for j, n in enumerate(Bi):
            v = ans[Aidx[km.labels_ == lab[j]], tgt[n]]; v = v[v >= 0]; u, c = np.unique(v, return_counts=True)
            lt.append(truth[n] == (u[c.argmax()] if len(v) else mode[tgt[n]]))
        lt = np.array(lt, float)
        path = json.load(open(f"outputs/suite/{ds}/greedy_bigfive.json")); best = tuple(max(path, key=lambda s: s["accA"])["subset"])
        tv = (predict(table(ds, "bigfive", best, rep, None), idx, rep, ans, tgt) == truth)[B].astype(float)
        vt = vt[B].astype(float)
        lines.append((ds, 100 * m.mean(), 100 * tv.mean(), 100 * vt.mean(), 100 * vd.mean(), 100 * lt.mean()))
        for name, base in (("type vector", tv), ("learned types", lt)):
            e, a, b, p = boot(vt - base); tests.append([ds, name, e, a, b, p])
    order = sorted(range(len(tests)), key=lambda i: tests[i][5]); adj = [0.0] * len(tests); run = 0.0
    for r, i in enumerate(order): run = max(run, min(1.0, (len(tests) - r) * tests[i][5])); adj[i] = run
    print("| Survey | Most common answer | Type vector | Verbal types | Verbal types, data assignment | Learned types |\n|---|---|---|---|---|---|")
    for l in lines: print(f"| {l[0]} | {l[1]:.1f} | {l[2]:.1f} | {l[3]:.1f} | {l[4]:.1f} | {l[5]:.1f} |")
    print("\n| Survey | Verbal types minus | Gain | 95% CI | Holm p |\n|---|---|---|---|---|")
    for t, a in zip(tests, adj): print(f"| {t[0]} | {t[1]} | {t[2]:+.1f} | {t[3]:+.1f} to {t[4]:+.1f} | {a:.4f} |")
    beat = sum(1 for t, a in zip(tests, adj) if t[1] == "type vector" and t[2] > 0 and a < .05)
    worse = sum(1 for t, a in zip(tests, adj) if t[1] == "learned types" and t[2] < 0 and a < .05)
    print(f"\nVerbal types beat type vectors on {beat} of {len(lines)}; fall clearly below learned types on {worse} of {len(lines)}. Descriptions with digits: {digits} of {K*len(lines)}.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset"); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--analyze", nargs="*"); a = ap.parse_args()
    if a.analyze is not None: analyze(a.analyze)
    else:
        from input_systems.provider import GeminiClient
        build(a.dataset, GeminiClient("gemini-3.5-flash", workers=a.workers))
