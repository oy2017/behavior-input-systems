"""Round trip: how much of a real group's behavior survives a description of it?

Groups of respondents are learned from data (27 k-means groups on half A, as in type_vector_diagnostics.py). Each group
is described to the model in one of several ways, always leaving out the item being predicted, and the model answers
that item as the described person. Scoring is on half B people, each assigned to the group the data puts them in
("data assignment"; the clean round trip) and, secondarily, to the description whose answers best match their other
answers ("fitted", the type-vector rule).

Conditions (Gemini 3.5 Flash, thinking off, 3 draws per item, median taken):
- prose12:  a second-person sketch written by the model from the 12 items (other than the target) on which the group
            differs most from everyone; at most 80 words, no numbers, no quoted items.
- proseall: the same from all items other than the target; at most 200 words.
- verbal:   every item other than the target with the group's typical answer given as the scale label.
- numeric:  every item other than the target with the group's typical answer given as the number (history format).
- moderate: prose12 plus one sentence telling the model to answer as a typical, not extreme, member.
- elicit:   prose12, but the model is asked what percentage of such people choose each option; the top option is the
            prediction.
- think:    prose12 answered with thinking on, on npas, mach, dass and nis only.

DECISION RULES, committed before any result of this experiment was computed. Accuracy is under data assignment on half
B, paired bootstrap over people, 10,000 resamples, Holm within each family, alpha 0.05.
- F1 richness: proseall, verbal and numeric each minus prose12, per survey (24 tests). Richer descriptions "help" if
  numeric minus prose12 is positive and significant on at least 6 of 8 surveys.
- F2 ceiling: learned groups minus numeric and minus verbal, per survey (16 tests). The model "cannot generalize from a
  complete profile" if learned minus numeric is positive and significant on at least 6 of 8. The loss "was
  summarization" if numeric is within 2 points of learned groups, or not significantly below it, on at least 6 of 8.
- Mechanism: extremity ratio (mean |z| of the model's typical answers over mean |z| of the group's typical answers,
  z-scored against half A), direction agreement on items where the group departs by more than 0.3 sd, and the mean
  per-group correlation of the two z patterns. Reported with bootstrap CIs over groups; no test.
- F3 fixes (48 tests): damped minus undamped for prose12, proseall, verbal, numeric, where the damping factor is that
  condition's extremity ratio computed from half A only; moderate minus prose12; elicit minus prose12. A fix "works" if
  it is positive and significant on at least 6 of 8 surveys and never significantly negative.
- F4 reasoning (4 tests): think minus prose12. Reasoning "helps" if positive and significant on at least 3 of 4.
- Population level (descriptive, no test): for each item, a synthetic sample is built from the 27 described groups,
  each group's draws weighted by its size, and compared with the real half B answer distribution by the Wasserstein-1
  distance as a percentage of the scale range (mean over items), and by the ratio of synthetic to real standard
  deviation. References: the most common answer (a point mass), learned groups (each group's most common answer,
  weighted by size), and type vectors (each type's median answers, weighted by how many half B people fit that type).
Anything not listed here is exploratory and will be labeled so."""
from __future__ import annotations
import argparse, json, re, sys, time, warnings
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from trait_search_greedy import table, predict
from verbalized_types import learned, K
from input_systems.suite import item_prompt, parse_int, scale_text
warnings.filterwarnings("ignore")
DRAWS = 3
ALL = ["npas", "riasec", "mach", "dass", "fti", "nis", "gss2022", "wvs7"]
THINK_DS = ["npas", "mach", "dass", "nis"]
NAME = {"npas": "Nerdiness", "riasec": "Vocational interests", "mach": "Machiavellianism", "dass": "Distress",
        "fti": "Temperament", "nis": "Nonverbal behavior", "gss2022": "General Social Survey", "wvs7": "World Values Survey"}
DESC_SYS = "You are a psychologist who summarizes groups of survey respondents."
MODERATE = ("Answer as a typical member of this group, not an extreme example. Most people, in any group, give moderate "
            "answers to most questions; the description above only highlights what makes the group distinctive.")

def stats(ds):
    people, rep, idx, ans, tgt, truth, A, B, keys, km, X = learned(ds)
    H = ans[A].astype(float); H[ans[A] < 0] = np.nan
    M = np.array([np.nanmean(H[km.labels_ == c], 0) for c in range(K)]); G = np.array([np.nanmedian(H[km.labels_ == c], 0) for c in range(K)])
    return dict(people=people, rep=rep, idx=idx, ans=ans, tgt=tgt, truth=truth, A=A, B=B, keys=keys, km=km, X=X, H=H,
                mu=np.nanmean(H, 0), sd=np.nanstd(H, 0) + 1e-9, M=M, G=G, size=np.bincount(km.labels_, minlength=K), I=len(keys))

def label(sc, v):
    labs = {int(k): t for k, t in sc["labels"].items()}
    if v in labs: return f'"{labs[v]}"'
    lo = max([k for k in labs if k < v], default=None); hi = min([k for k in labs if k > v], default=None)
    return f'between "{labs[lo]}" and "{labs[hi]}"' if lo is not None and hi is not None else str(v)

def desc_user(S, c, t, cond):
    z = (S["M"][c] - S["mu"]) / S["sd"]; z[t] = 0
    order = [i for i in np.argsort(-np.abs(np.nan_to_num(z))) if i != t]
    if cond == "prose12": order = order[:12]
    lines = []
    for i in order:
        k = S["keys"][i]; sc = S["rep"][k]["scale"]; txt = S["rep"][k]["items"][k]["text"]
        lines.append(f'- "{txt}" ({sc["min"]} to {sc["max"]}): this group averages {S["M"][c, i]:.1f}, everyone averages {S["mu"][i]:.1f}')
    n, pct = S["size"][c], 100 * S["size"][c] / S["A"].sum()
    if cond == "prose12":
        head = f"Below are the questionnaire items on which one group of respondents ({n} people, {pct:.0f}% of all) differs most from everyone else."
        length = "Use 3 to 5 sentences and at most 80 words."
    else:
        head = f"Below are all the questionnaire items, ordered by how much one group of respondents ({n} people, {pct:.0f}% of all) differs from everyone else on them."
        length = "Use 6 to 10 sentences and at most 200 words. Cover the whole picture, not only the top items."
    return (head + "\n\n" + "\n".join(lines) + "\n\nWrite a description of a typical person in this group, addressed to them in the "
            "second person (\"You are someone who...\"). Describe their dispositions, values, habits or tendencies. " + length +
            " Do not use numbers and do not quote or list the questionnaire items.")

def desc_path(ds, cond): return Path(f"outputs/suite/{ds}/roundtrip_desc_{cond}.jsonl")

def load_desc(ds, cond):
    p = desc_path(ds, cond)
    return {(d["cluster"], d["target"]): d["text"] for d in map(json.loads, open(p))} if p.exists() else {}

def ensure_desc(ds, S, cond, client):
    need = K * S["I"]; have = load_desc(ds, cond)
    if len(have) >= need: return have
    if client is None:
        while len(have) < need: time.sleep(60); have = load_desc(ds, cond)
        return have
    jobs = [(c, t) for c in range(K) for t in range(S["I"]) if (c, t) not in have]
    rows = client.map(jobs, lambda j: {"cluster": j[0], "target": j[1], "text": client.complete(DESC_SYS, desc_user(S, j[0], j[1], cond), sample=0).strip()})
    with open(desc_path(ds, cond), "a") as f:
        for d in rows: f.write(json.dumps(d) + "\n")
    return load_desc(ds, cond)

def profile(S, c, t, numeric):
    lines = []
    for i, k in enumerate(S["keys"]):
        if i == t or np.isnan(S["G"][c, i]): continue
        v = int(np.round(S["G"][c, i])); sc = S["rep"][k]["scale"]; txt = S["rep"][k]["items"][k]["text"]
        lines.append(f"- {txt} ({sc['min']} to {sc['max']}) Answer: [{v}]" if numeric else f"- {txt} Answer: {label(sc, v)}")
    return ("You are a typical member of a group of survey respondents. Members of your group typically answered the "
            "following items as follows:\n" + "\n".join(lines))

def elicit_user(r, k):
    return (f"Consider people like the one described above. For the following item, what percentage of them would choose each "
            f"option {scale_text(r['scale'])}?\n\nItem: {r['items'][k]['text']}\n\nReply with only a JSON object mapping each option "
            f"number to a percentage, for example {{\"{r['scale']['min']}\": 40, \"{r['scale']['max']}\": 10}}.")

def parse_dist(text, sc):
    m = re.search(r"\{.*\}", text, re.S)
    if not m: return None
    try: d = json.loads(m.group(0))
    except Exception: return None
    out = {}
    for k, v in d.items():
        try: kk = int(float(str(k).strip())); vv = float(v)
        except Exception: continue
        if sc["min"] <= kk <= sc["max"] and vv >= 0: out[kk] = vv
    if not out or sum(out.values()) <= 0: return None
    return out

def ans_path(ds, cond): return Path(f"outputs/type_table/search/{ds}/roundtrip__{cond}.jsonl")

def build(ds, cond, client):
    t0 = time.time(); S = stats(ds); rep, keys = S["rep"], S["keys"]
    desc = ensure_desc(ds, S, "proseall", client) if cond == "proseall" else (ensure_desc(ds, S, "prose12", client if cond == "prose12" else None) if cond in ("prose12", "moderate", "elicit", "think") else None)
    def system(c, t):
        base = rep[keys[t]]["base_system"]
        if cond in ("prose12", "proseall", "think"): return base + "\n\n" + desc[(c, t)]
        if cond == "moderate": return base + "\n\n" + desc[(c, t)] + "\n\n" + MODERATE
        if cond == "elicit": return "Here is a description of a typical member of a group of people who answered an online questionnaire, written as if addressed to them:\n\n" + desc[(c, t)]
        return base + "\n\n" + profile(S, c, t, cond == "numeric")
    path = ans_path(ds, cond); have = {(d["cluster"], d["item"], d.get("sample", 0)) for d in map(json.loads, open(path))} if path.exists() else set()
    draws = 1 if cond == "elicit" else DRAWS
    jobs = [(c, t, s) for c in range(K) for t in range(S["I"]) for s in range(draws) if (c, keys[t], s) not in have]
    def run(job):
        c, t, s = job; r = rep[keys[t]]; sc = r["scale"]
        if cond == "elicit":
            return {"cluster": c, "item": keys[t], "sample": 0, "dist": parse_dist(client.complete(system(c, t), elicit_user(r, keys[t]), sample=0), sc)}
        return {"cluster": c, "item": keys[t], "sample": s, "choice": parse_int(client.complete(system(c, t), item_prompt(r, keys[t]), sample=s), sc["min"], sc["max"])}
    with open(path, "a") as f:
        for i in range(0, len(jobs), 2000):
            for d in client.map(jobs[i:i + 2000], run): f.write(json.dumps(d) + "\n")
            f.flush()
    print(f"finished {ds} {cond} ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)

def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0.0] * len(ps); run = 0.0
    for r, i in enumerate(order): run = max(run, min(1.0, (len(ps) - r) * ps[i])); adj[i] = run
    return adj

def analyze(datasets, conds):
    rng = np.random.default_rng(0); out = {}; fam = {"F1": [], "F2": [], "F3": [], "F4": []}
    def boot(d):
        b = 100 * d[rng.integers(0, len(d), (10000, len(d)))].mean(1)
        return 100 * d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    for ds in datasets:
        S = stats(ds); I, keys, rep, ans, tgt, truth, A, B, km, X = S["I"], S["keys"], S["rep"], S["ans"], S["tgt"], S["truth"], S["A"], S["B"], S["km"], S["X"]
        mu, sd, G = S["mu"], S["sd"], S["G"]; lo = np.array([rep[k]["scale"]["min"] for k in keys]); hi = np.array([rep[k]["scale"]["max"] for k in keys])
        Bi = np.where(B)[0]; Aidx = np.where(A)[0]; obs = ans >= 0; C = km.cluster_centers_
        lab = np.array([np.nanargmin([np.nanmean(np.where(obs[n] & (np.arange(I) != tgt[n]), (X[n] - C[k]) ** 2, np.nan)) for k in range(K)]) for n in Bi])
        mode = np.array([np.bincount(ans[A, i][ans[A, i] >= 0]).argmax() for i in range(I)])
        acc = lambda pred: (np.asarray(pred) == truth[Bi]).astype(float)
        m = acc(mode[tgt[Bi]])
        lt = acc([(lambda v: np.bincount(v).argmax() if len(v) else mode[tgt[n]])(ans[Aidx[km.labels_ == lab[j]], tgt[n]][ans[Aidx[km.labels_ == lab[j]], tgt[n]] >= 0]) for j, n in enumerate(Bi)])
        gpath = json.load(open(f"outputs/suite/{ds}/greedy_bigfive.json")); best = tuple(max(gpath, key=lambda s: s["accA"])["subset"])
        tv = (predict(table(ds, "bigfive", best, rep, None), idx := S["idx"], rep, ans, tgt) == truth)[B].astype(float)
        res = {"mode": m.mean() * 100, "learned": lt.mean() * 100, "type_vector": tv.mean() * 100, "n_B": len(Bi), "cond": {}}
        zG = (G - mu) / sd
        size = S["size"]
        def hist(vals, w, i):
            h = np.zeros(hi[i] - lo[i] + 1)
            for v, ww in zip(vals, w):
                if not np.isnan(v): h[int(v) - lo[i]] += ww
            return h / h.sum() if h.sum() > 0 else None
        def wsd(real, synth, i):
            if synth is None: return np.nan, np.nan
            vals = np.arange(lo[i], hi[i] + 1); W = 100 * np.abs(np.cumsum(real) - np.cumsum(synth)).sum() / max(1, hi[i] - lo[i])
            sdr = np.sqrt(((vals - (vals * synth).sum()) ** 2 * synth).sum()); sdt = np.sqrt(((vals - (vals * real).sum()) ** 2 * real).sum())
            return W, sdr / sdt if sdt > 0 else np.nan
        real = [hist(ans[Bi, i][ans[Bi, i] >= 0], np.ones((ans[Bi, i] >= 0).sum()), i) for i in range(I)]
        def pop(hists):  # hists: list per item of synthetic hist
            ws = [wsd(real[i], hists[i], i) for i in range(I) if real[i] is not None]
            return np.nanmean([w for w, _ in ws]), np.nanmean([r for _, r in ws])
        res["W"] = {}; res["sd_ratio"] = {}
        res["W"]["mode"], res["sd_ratio"]["mode"] = pop([hist([mode[i]], [1.0], i) for i in range(I)])
        gmode = np.array([[(lambda v: np.bincount(v).argmax() if len(v) else mode[i])(ans[Aidx[km.labels_ == c], i][ans[Aidx[km.labels_ == c], i] >= 0]) for i in range(I)] for c in range(K)])
        res["W"]["learned"], res["sd_ratio"]["learned"] = pop([hist(gmode[:, i], size, i) for i in range(I)])
        tdraws = table(ds, "bigfive", best, rep, None); types = sorted({t for t, _ in tdraws}); T = np.full((len(types), I), np.nan)
        for a_, t_ in enumerate(types):
            for i, k in enumerate(keys):
                if (t_, k) in tdraws: T[a_, i] = np.median(tdraws[(t_, k)])
        fitc = np.zeros(len(types))
        for n in Bi:
            o = obs[n].copy(); o[tgt[n]] = False; fitc[np.nanargmin(np.nanmean(np.abs(T[:, o] - ans[n, o]) / (hi - lo)[o], 1))] += 1
        res["W"]["type_vector"], res["sd_ratio"]["type_vector"] = pop([hist(T[:, i], fitc, i) for i in range(I)])
        def mech(R):
            zR = (R - mu) / sd; ok = ~np.isnan(zR) & ~np.isnan(zG); big = ok & (np.abs(zG) > 0.3)
            ratio = np.nanmean(np.abs(zR[ok])) / np.nanmean(np.abs(zG[ok]))
            rb = [np.nanmean(np.abs(zR[g][ok[g]])) / np.nanmean(np.abs(zG[g][ok[g]])) for g in rng.integers(0, K, (2000, K))]
            agree = np.mean(np.sign(zR[big]) == np.sign(zG[big])); corr = np.nanmean([np.corrcoef(zR[c][ok[c]], zG[c][ok[c]])[0, 1] for c in range(K) if ok[c].sum() > 3])
            return ratio, np.percentile(rb, 2.5), np.percentile(rb, 97.5), 100 * agree, corr
        acc_cond = {}
        for cond in conds:
            p = ans_path(ds, cond)
            if not p.exists() or (cond == "think" and ds not in THINK_DS): continue
            rows = [json.loads(l) for l in open(p)]
            if cond == "elicit":
                E = {(d["cluster"], d["item"]): d["dist"] for d in rows if d["dist"]}
                R = np.full((K, I), np.nan); EV = np.full((K, I), np.nan)
                for (c, k), dist in E.items():
                    i = idx[k]; R[c, i] = max(dist, key=dist.get); tot = sum(dist.values()); EV[c, i] = sum(v * w for v, w in dist.items()) / tot
                a = acc(np.where(np.isnan(R[lab, tgt[Bi]]), mode[tgt[Bi]], R[lab, tgt[Bi]])); ratio, r_lo, r_hi, agree, corr = mech(R)
                a_ev = acc(np.where(np.isnan(EV[lab, tgt[Bi]]), mode[tgt[Bi]], np.clip(np.round(EV[lab, tgt[Bi]]), lo[tgt[Bi]], hi[tgt[Bi]])))
                res["cond"][cond] = {"acc_data": 100 * a.mean(), "acc_ev": 100 * a_ev.mean(), "parsed": 100 * len(E) / (K * I), "ratio": ratio, "ratio_ci": [r_lo, r_hi], "agree": agree, "corr": corr}
                hs = []
                for i, k in enumerate(keys):
                    h = np.zeros(hi[i] - lo[i] + 1)
                    for c in range(K):
                        if (c, k) in E:
                            dist = E[(c, k)]; tot = sum(dist.values())
                            for v, w in dist.items(): h[v - lo[i]] += size[c] * w / tot
                    hs.append(h / h.sum() if h.sum() > 0 else None)
                res["W"][cond], res["sd_ratio"][cond] = pop(hs)
                acc_cond[cond] = a; continue
            draws = {}
            for d in rows:
                if d["choice"] is not None: draws.setdefault((f"c{d['cluster']:02d}", d["item"]), []).append(d["choice"])
            R = np.full((K, I), np.nan)
            for (c, k), v in draws.items(): R[int(c[1:]), idx[k]] = np.median(v)
            pred = R[lab, tgt[Bi]]; a = acc(np.where(np.isnan(pred), mode[tgt[Bi]], pred))
            fit = (predict(draws, idx, rep, ans, tgt) == truth)[B].astype(float)
            ratio, r_lo, r_hi, agree, corr = mech(R)
            Rd = np.clip(np.round(mu + (R - mu) / ratio), lo, hi); pd = Rd[lab, tgt[Bi]]; ad = acc(np.where(np.isnan(pd), mode[tgt[Bi]], pd))
            res["cond"][cond] = {"acc_data": 100 * a.mean(), "acc_fit": 100 * fit.mean(), "acc_damped": 100 * ad.mean(), "ratio": ratio, "ratio_ci": [r_lo, r_hi],
                                 "agree": agree, "corr": corr, "parsed": 100 * sum(len(v) for v in draws.values()) / (K * I * DRAWS)}
            acc_cond[cond] = a; acc_cond[cond + "_damped"] = ad
            hs = []
            for i, k in enumerate(keys):
                vals, w = [], []
                for c in range(K):
                    for v in draws.get((f"c{c:02d}", k), []): vals.append(v); w.append(size[c] / len(draws[(f"c{c:02d}", k)]))
                hs.append(hist(vals, w, i) if vals else None)
            res["W"][cond], res["sd_ratio"][cond] = pop(hs)
            if cond in ("prose12", "proseall", "verbal", "numeric"): fam["F3"].append([ds, f"{cond} damped minus {cond}", *boot(ad - a)])
        if "prose12" in acc_cond:
            for c2 in ("proseall", "verbal", "numeric"):
                if c2 in acc_cond: fam["F1"].append([ds, f"{c2} minus prose12", *boot(acc_cond[c2] - acc_cond["prose12"])])
            for c2 in ("moderate", "elicit"):
                if c2 in acc_cond: fam["F3"].append([ds, f"{c2} minus prose12", *boot(acc_cond[c2] - acc_cond["prose12"])])
            if "think" in acc_cond: fam["F4"].append([ds, "think minus prose12", *boot(acc_cond["think"] - acc_cond["prose12"])])
        for c2 in ("numeric", "verbal"):
            if c2 in acc_cond: fam["F2"].append([ds, f"learned minus {c2}", *boot(lt - acc_cond[c2])])
        out[ds] = res
    cols = [c for c in conds if any(c in out[d]["cond"] for d in out)]
    print("Accuracy on half B, data assignment (%)\n| Survey | Most common | Type vector | " + " | ".join(cols) + " | Learned groups |\n|---|---|---|" + "---|" * len(cols) + "---|")
    for ds, r in out.items(): print(f"| {NAME[ds]} | {r['mode']:.1f} | {r['type_vector']:.1f} | " + " | ".join(f"{r['cond'][c]['acc_data']:.1f}" if c in r["cond"] else "" for c in cols) + f" | {r['learned']:.1f} |")
    print("\nDamped accuracy (factor from half A)\n| Survey | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols))
    for ds, r in out.items(): print(f"| {NAME[ds]} | " + " | ".join(f"{r['cond'][c]['acc_damped']:.1f}" if c in r["cond"] and "acc_damped" in r["cond"][c] else "" for c in cols) + " |")
    print("\nExtremity ratio, model over group [95% CI over groups]; direction agreement; pattern correlation\n| Survey | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols))
    for ds, r in out.items(): print(f"| {NAME[ds]} | " + " | ".join(f"{r['cond'][c]['ratio']:.2f} [{r['cond'][c]['ratio_ci'][0]:.2f}, {r['cond'][c]['ratio_ci'][1]:.2f}]; {r['cond'][c]['agree']:.0f}%; {r['cond'][c]['corr']:.2f}" if c in r["cond"] else "" for c in cols) + " |")
    print("\nFitted assignment accuracy (type-vector rule)\n| Survey | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols))
    for ds, r in out.items(): print(f"| {NAME[ds]} | " + " | ".join(f"{r['cond'][c]['acc_fit']:.1f}" if c in r["cond"] and "acc_fit" in r["cond"][c] else "" for c in cols) + " |")
    pc = ["mode", "type_vector"] + cols + ["learned"]
    print("\nPopulation level: Wasserstein distance of the synthetic sample to the real answers (% of scale; lower is better) / synthetic-to-real sd ratio\n| Survey | " + " | ".join(pc) + " |\n|---|" + "---|" * len(pc))
    for ds, r in out.items(): print(f"| {NAME[ds]} | " + " | ".join(f"{r['W'][c]:.1f} / {r['sd_ratio'][c]:.2f}" if c in r["W"] else "" for c in pc) + " |")
    for f, tests in fam.items():
        if not tests: continue
        adj = holm([t[5] for t in tests]); print(f"\n{f}\n| Survey | Test | Gain | 95% CI | Holm p |\n|---|---|---|---|---|")
        for t, a in zip(tests, adj): t.append(a); print(f"| {NAME[t[0]]} | {t[1]} | {t[2]:+.1f} | {t[3]:+.1f} to {t[4]:+.1f} | {a:.4f} |")
    out["tests"] = fam
    json.dump(out, open("outputs/roundtrip.json", "w"), indent=1, default=float)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dataset", nargs="*", default=ALL); ap.add_argument("--cond", nargs="*", default=["prose12"])
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--analyze", action="store_true"); a = ap.parse_args()
    if a.analyze: analyze(a.dataset, a.cond)
    else:
        from input_systems.provider import GeminiClient
        for cond in a.cond:
            client = GeminiClient("gemini-3.5-flash@think" if cond == "think" else "gemini-3.5-flash", workers=a.workers)
            for ds in (THINK_DS if cond == "think" else a.dataset):
                if ds in a.dataset: build(ds, cond, client)
