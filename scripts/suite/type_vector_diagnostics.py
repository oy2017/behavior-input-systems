"""Why do type vectors beat the most common answer on some surveys and not others? Diagnostics from stored tables and
answers only (no API calls), on the same scored people as the six-survey test (half B of records 1000 onward), using
the Big Five set chosen on half A for each survey.

1. Steerability: do trait levels move the model's answer? Share of items where all types give the same median; spread of
   type medians relative to the human answer spread for that item.
2. Reachability: share of people whose actual answer equals some type's median answer for that item.
3. Type usage: distinct fitted types, share of people on the three most used types, tie rate.
4. Best case: the type that fits a person best when the target item is included (an upper bound for this type set).
5. Data-learned types: 27 clusters learned from half A answers (k-means), each person assigned on their other items and
   predicted with the cluster's most common answer. Same number of types, but learned from data, not from trait words.
6. Structure: correlation between the human item-by-item correlation matrix and the model's (computed across types);
   share of human answer variance on the first principal component.
Cross-survey correlations use 8 surveys and are descriptive only."""
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trait_search_greedy import load, arrays, table, predict
warnings.filterwarnings("ignore")
rng = np.random.default_rng(0)

def type_matrix(draws, idx):
    vectors = sorted({k[0] for k in draws}); M = np.full((len(vectors), len(idx)), np.nan)
    for (vk, it), ds in draws.items():
        if it in idx: M[vectors.index(vk), idx[it]] = np.median(ds)
    return vectors, M

def best_type(draws, idx, rep, ans, tgt, include_target):
    vectors = sorted({k[0] for k in draws}); V, I = len(vectors), len(idx)
    glo = min(rep[k]["scale"]["min"] for k in idx); ghi = max(rep[k]["scale"]["max"] for k in idx); vals = np.arange(glo, ghi + 1)
    D = np.full((V, I, len(vals)), np.nan)
    for (vk, it), ds in draws.items():
        if it not in idx: continue
        sc = rep[it]["scale"]; arr = np.array(ds, float)
        D[vectors.index(vk), idx[it]] = np.abs(arr[None, :] - vals[:, None]).mean(1) / max(1, sc["max"] - sc["min"])
    N = len(ans); e = np.zeros((V, N)); a = np.clip(ans - glo, 0, len(vals) - 1); col = np.arange(I)[None, :]
    for v in range(V):
        d = D[v, col, a].copy(); d[ans < 0] = np.nan
        if not include_target: d[np.arange(N), tgt] = np.nan
        e[v] = np.nanmean(d, axis=1)
    best = np.nanmin(e, axis=0); return e, e <= best + 1e-12

rows = []
for ds in ["npas", "riasec", "mach", "dass", "fti", "nis", "gss2022", "wvs7"]:
    people, rep, idx = load(ds); ans, tgt, truth = arrays(people, idx); A = np.arange(len(people)) % 2 == 0; B = ~A
    I = len(idx); rngs = np.array([max(1, rep[k]["scale"]["max"] - rep[k]["scale"]["min"]) for k in sorted(idx, key=idx.get)])
    mode = {}
    for i in range(I):
        v = ans[A, i]; v = v[v >= 0]; u, c = np.unique(v, return_counts=True); mode[i] = u[c.argmax()]
    m_hit = np.array([truth[n] == mode[tgt[n]] for n in range(len(people))])[B]
    sub = {}
    for pool in ("bigfive", "placebo"):
        path = json.load(open(f"outputs/suite/{ds}/greedy_{pool}.json")); sub[pool] = tuple(max(path, key=lambda s: s["accA"])["subset"])
    dr = table(ds, "bigfive", sub["bigfive"], rep, None); pr = table(ds, "placebo", sub["placebo"], rep, None)
    bf = predict(dr, idx, rep, ans, tgt); pl = predict(pr, idx, rep, ans, tgt)
    bf_hit = (bf == truth)[B]; pl_hit = (pl == truth)[B]
    vectors, M = type_matrix(dr, idx)
    # 1 steerability
    flat = float(np.mean([np.nanmax(M[:, i]) == np.nanmin(M[:, i]) for i in range(I)]))
    hum_sd = np.array([ans[A, i][ans[A, i] >= 0].std() for i in range(I)]); steer = float(np.nanmean(np.nanstd(M, axis=0) / np.maximum(hum_sd, 1e-9)))
    # 2 reachability
    reach = float(np.mean([truth[n] in set(np.round(M[:, tgt[n]][~np.isnan(M[:, tgt[n]])]).astype(int)) for n in np.where(B)[0]]))
    # 3 type usage
    _, tied = best_type(dr, idx, rep, ans, tgt, False); first = tied.argmax(0)[B]
    u, c = np.unique(first, return_counts=True); top3 = float(np.sort(c)[::-1][:3].sum() / B.sum()); ties = float((tied[:, B].sum(0) > 1).mean())
    # 4 best case: type chosen with the target included
    _, tied_o = best_type(dr, idx, rep, ans, tgt, True); mo = M[:, tgt].copy(); mo[~tied_o] = np.nan
    oracle = float((np.round(np.nanmean(mo, 0)) == truth)[B].mean())
    # 5 data-learned types: 27 k-means clusters on half A, scaled by item range, missing filled with item mean
    X = ans.astype(float); X[ans < 0] = np.nan; col_mean = np.nanmean(X[A], 0); X = np.where(np.isnan(X), col_mean, X) / rngs
    km = KMeans(n_clusters=27, n_init=10, random_state=0).fit(X[A]); C = km.cluster_centers_
    labA = km.labels_; Bi = np.where(B)[0]; obs = (ans >= 0)
    dist = np.array([[np.nanmean(np.where(obs[n] & (np.arange(I) != tgt[n]), (X[n] - C[k]) ** 2, np.nan)) for k in range(27)] for n in Bi])
    lab = dist.argmin(1); km_hit = []
    Aidx = np.where(A)[0]
    for j, n in enumerate(Bi):
        mem = Aidx[labA == lab[j]]; v = ans[mem, tgt[n]]; v = v[v >= 0]
        km_hit.append(truth[n] == (np.unique(v, return_counts=True)[0][np.unique(v, return_counts=True)[1].argmax()] if len(v) else mode[tgt[n]]))
    km_hit = np.array(km_hit, float)
    # 6 structure
    H = np.array(ans[A], float); H[ans[A] < 0] = np.nan
    import pandas as pd
    hc = pd.DataFrame(H).corr(min_periods=50).values; mc = pd.DataFrame(M).corr().values
    iu = np.triu_indices(I, 1); ok = ~np.isnan(hc[iu]) & ~np.isnan(mc[iu])
    align = float(np.corrcoef(hc[iu][ok], mc[iu][ok])[0, 1]); ev = np.linalg.eigvalsh(np.nan_to_num(hc, nan=0.0) + np.eye(I) * 0)[::-1]; pc1 = float(ev[0] / I)
    # spread of predictions
    sd_ratio = float(np.nanstd(bf[B]) / np.std(truth[B]))
    def ci(d):
        b = 100 * d[rng.integers(0, len(d), (10000, len(d)))].mean(1); return f"{100*d.mean():+.1f} ({np.percentile(b,2.5):+.1f}, {np.percentile(b,97.5):+.1f})"
    km2 = KMeans(n_clusters=27, n_init=10, random_state=1).fit(X[A])
    print(f"  {ds}: learned-types minus type-vector {ci(km_hit - bf_hit)} | learned-types minus mode {ci(km_hit - m_hit)} | type-vector minus mode {ci(bf_hit.astype(float) - m_hit)} | kmeans inertia seeds 0/1 {km.inertia_:.0f}/{km2.inertia_:.0f}", flush=True)
    rows.append(dict(ds=ds, n=int(B.sum()), items=I, mode=100 * m_hit.mean(), placebo=100 * pl_hit.mean(), bigfive=100 * bf_hit.mean(), gain=100 * (bf_hit.mean() - m_hit.mean()),
                     kmeans27=100 * km_hit.mean(), oracle=100 * oracle, reach=100 * reach, flat_items=100 * flat, steer=steer, distinct=int(len(u)), top3=100 * top3, ties=100 * ties,
                     align=align, pc1=100 * pc1, sd_ratio=sd_ratio, subset="+".join(s[:4] for s in sub["bigfive"])))
    print(f"done {ds}", flush=True)
cols = ["ds", "subset", "mode", "placebo", "bigfive", "gain", "kmeans27", "oracle", "reach", "flat_items", "steer", "distinct", "top3", "ties", "align", "pc1", "sd_ratio"]
print("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
for r in rows: print("| " + " | ".join(f"{r[c]:.2f}" if isinstance(r[c], float) else str(r[c]) for c in cols) + " |")
print("\nSpearman across 8 surveys, gain over most common answer vs each diagnostic (descriptive, n = 8):")
for c in ["kmeans27", "oracle", "reach", "flat_items", "steer", "distinct", "top3", "align", "pc1", "sd_ratio"]:
    rho, p = spearmanr([r["gain"] for r in rows], [r[c] for r in rows]); print(f"  {c:10s} rho={rho:+.2f} (p={p:.2f})")
print("Spearman, data-learned types minus mode vs PC1 share:", spearmanr([r["kmeans27"] - r["mode"] for r in rows], [r["pc1"] for r in rows]))
Path("outputs/type_vector_diagnostics.json").write_text(json.dumps(rows, indent=1))
