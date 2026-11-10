"""The round trip for the type-vector recipe (Jackson et al. 2026), with the recipe's own unit.

The recipe matches a person to one of 27 types (three Big Five traits at three levels) by fit: the type whose generated
answers are nearest the person's other answers. So the real people behind a type are the people who fit it. Here:
- Groups: training-half people fitted to each type by the recipe's rule (target item masked).
- Group ceiling: the most common answer among a type's training members, given to test people fitted to that type.
- Fact list: a type's training members' typical answer to every other question (the number list), target withheld,
  answered by the model three times; median kept.
- Description under test: the type vector itself, as already run (outputs/type_table/search/<ds>/bigfive__*).
Scoring: test-half people, each fitted to a type by the recipe's rule, accuracy on the held-out answer.

RULE, committed before running: per questionnaire, fact list minus type vector (the description's loss) and group
ceiling minus fact list (the model's loss), paired bootstrap over test people, Holm over 8 within each family. The
type vector "loses" if fact list minus type vector is positive and significant on at least 6 of 8."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from trait_search_greedy import table, predict
from roundtrip import stats, NAME, DRAWS
from input_systems.suite import item_prompt, parse_int
ALL = ["npas", "riasec", "mach", "dass", "fti", "nis", "gss2022", "wvs7"]

def fit_types(ds, S):
    """Fit every person (training and test) to a type by the recipe's rule; return type names, per-person type index, and the type table medians."""
    gpath = json.load(open(f"outputs/suite/{ds}/greedy_bigfive.json")); best = tuple(max(gpath, key=lambda s: s["accA"])["subset"])
    tdraws = table(ds, "bigfive", best, S["rep"], None); types = sorted({t for t, _ in tdraws}); I = S["I"]; keys = S["keys"]
    T = np.full((len(types), I), np.nan)
    for a, t in enumerate(types):
        for i, k in enumerate(keys):
            if (t, k) in tdraws: T[a, i] = np.median(tdraws[(t, k)])
    lo = np.array([S["rep"][k]["scale"]["min"] for k in keys]); hi = np.array([S["rep"][k]["scale"]["max"] for k in keys])
    ans, tgt, obs = S["ans"], S["tgt"], S["ans"] >= 0
    fit = np.full(len(ans), -1)
    for n in range(len(ans)):
        o = obs[n].copy(); o[tgt[n]] = False
        if o.sum() == 0: continue
        fit[n] = int(np.nanargmin(np.nanmean(np.abs(T[:, o] - ans[n, o]) / (hi - lo)[o], 1)))
    return types, fit, T

def type_profile(S, members, t):
    H = S["ans"][members].astype(float); H[S["ans"][members] < 0] = np.nan; G = np.nanmedian(H, 0)
    lines = []
    for i, k in enumerate(S["keys"]):
        if i == t or np.isnan(G[i]): continue
        sc = S["rep"][k]["scale"]; lines.append(f"- {S['rep'][k]['items'][k]['text']} ({sc['min']} to {sc['max']}) Answer: [{int(np.round(G[i]))}]")
    return "You are a typical member of a group of survey respondents. Members of your group typically answered the following items as follows:\n" + "\n".join(lines)

def build(ds, client):
    t0 = time.time(); S = stats(ds); types, fit, T = fit_types(ds, S); A = S["A"]; keys = S["keys"]; rep = S["rep"]
    members = {a: np.where(A & (fit == a))[0] for a in range(len(types))}
    out = Path(f"outputs/type_table/search/{ds}/tvroundtrip__numeric.jsonl")
    have = {(d["type"], d["item"], d["sample"]) for d in map(json.loads, open(out))} if out.exists() else set()
    jobs = [(a, t, s) for a in range(len(types)) if len(members[a]) >= 5 for t in range(S["I"]) for s in range(DRAWS) if (a, keys[t], s) not in have]
    def run(job):
        a, t, s = job; r = rep[keys[t]]; sc = r["scale"]
        text = client.complete(r["base_system"] + "\n\n" + type_profile(S, members[a], t), item_prompt(r, keys[t]), sample=s)
        return {"type": a, "item": keys[t], "sample": s, "choice": parse_int(text, sc["min"], sc["max"])}
    with open(out, "a") as f:
        for i in range(0, len(jobs), 2000):
            for d in client.map(jobs[i:i + 2000], run): f.write(json.dumps(d) + "\n")
            f.flush()
    print(f"finished {ds} tvroundtrip ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)

def analyze():
    rng = np.random.default_rng(0); rows = []; tests = {"desc": [], "model": []}
    def boot(d):
        b = 100 * d[rng.integers(0, len(d), (10000, len(d)))].mean(1)
        return 100 * d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    def holm(ps):
        order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0.0] * len(ps); run = 0.0
        for r, i in enumerate(order): run = max(run, min(1.0, (len(ps) - r) * ps[i])); adj[i] = run
        return adj
    for ds in ALL:
        S = stats(ds); types, fit, T = fit_types(ds, S); A, B, ans, tgt, truth, I, keys = S["A"], S["B"], S["ans"], S["tgt"], S["truth"], S["I"], S["keys"]
        Bi = np.where(B)[0]; mode = np.array([np.bincount(ans[A, i][ans[A, i] >= 0]).argmax() for i in range(I)])
        R = np.full((len(types), I), np.nan); d = {}
        for l in open(f"outputs/type_table/search/{ds}/tvroundtrip__numeric.jsonl"):
            r = json.loads(l)
            if r["choice"] is not None: d.setdefault((r["type"], r["item"]), []).append(r["choice"])
        for (a, k), v in d.items(): R[a, S["idx"][k]] = np.median(v)
        floor = (mode[tgt[Bi]] == truth[Bi]).astype(float)
        tv = (T[fit[Bi], tgt[Bi]] == truth[Bi]).astype(float)
        fl = np.array([R[fit[n], tgt[n]] if not np.isnan(R[fit[n], tgt[n]]) else mode[tgt[n]] for n in Bi]) == truth[Bi]; fl = fl.astype(float)
        ceil = []
        for n in Bi:
            v = ans[np.where(A & (fit == fit[n]))[0], tgt[n]]; v = v[v >= 0]; ceil.append((np.bincount(v).argmax() if len(v) else mode[tgt[n]]) == truth[n])
        ceil = np.array(ceil, float)
        rows.append((ds, 100 * floor.mean(), 100 * tv.mean(), 100 * fl.mean(), 100 * ceil.mean()))
        tests["desc"].append([ds, *boot(fl - tv)]); tests["model"].append([ds, *boot(ceil - fl)])
    print("Type-vector round trip, the recipe's own unit (types fitted by the recipe's rule); accuracy on test people (%)")
    print("| Questionnaire | Floor | Type vector | Fact list of the type's people | Type ceiling | Description's loss | Model's loss |\n|---|---|---|---|---|---|---|")
    for ds, f, t, l, c in rows: print(f"| {NAME[ds]} | {f:.1f} | {t:.1f} | {l:.1f} | {c:.1f} | {l-t:+.1f} | {c-l:+.1f} |")
    for name, ts in tests.items():
        adj = holm([t[4] for t in ts]); print(f"\n{'Description: fact list minus type vector' if name=='desc' else 'Model: type ceiling minus fact list'}\n| Questionnaire | Gain | 95% CI | Holm p |\n|---|---|---|---|")
        for t, a in zip(ts, adj): print(f"| {NAME[t[0]]} | {t[1]:+.1f} | {t[2]:+.1f} to {t[3]:+.1f} | {a:.4f} |")
        print(f"Significantly positive on {sum(1 for t,a in zip(ts,adj) if t[1]>0 and a<.05)} of {len(ts)}.")
    json.dump({"rows": rows, "tests": tests}, open("outputs/type_vector_roundtrip.json", "w"), indent=1, default=float)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", nargs="*", default=ALL); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--analyze", action="store_true"); a = ap.parse_args()
    if a.analyze: analyze()
    else:
        from input_systems.provider import GeminiClient
        client = GeminiClient("gemini-3.5-flash", workers=a.workers)
        for ds in a.dataset: build(ds, client)
