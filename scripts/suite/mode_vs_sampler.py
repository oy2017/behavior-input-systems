"""One-draw accuracy with demographics against two benchmarks, from existing outputs (no API calls).
mode = always answer the item's most common answer in the training pool.
sampler = expected accuracy of drawing one answer from the item's training-pool distribution, so a person's
hit probability is p(their answer). A perfectly calibrated one-draw simulator with no information about the
person scores this, which is below the mode by construction. Intervals: record bootstrap, 4,000 resamples."""
import json
import numpy as np
rng = np.random.default_rng(0)
print("| Dataset | demographics | mode | sampler | demographics - mode (95% CI) | demographics - sampler (95% CI) |\n|---|---|---|---|---|---|")
for d in ["bigfive", "mach", "dass", "npas", "riasec", "fti", "nis", "gss2022", "wvs7"]:
    BR = json.load(open(f"data/suite_baserates/{d}.json"))["items"]
    a, m, s = [], [], []
    for r in map(json.loads, open(f"outputs/suite/{d}/gemini-3.5-flash/demographics.jsonl")):
        e = BR.get(r["target_item"])
        if not e or r["prediction"] is None: continue
        p, t = e["pop"], str(r["truth"])
        a.append(r["prediction"] == r["truth"]); m.append(t == max(p, key=p.get)); s.append(p.get(t, 0.0))
    a, m, s = (np.array(x, float) for x in (a, m, s))
    idx = rng.integers(0, len(a), (4000, len(a)))
    ci = lambda x: np.percentile(x[idx].mean(1), [2.5, 97.5]) * 100
    c1, c2 = ci(a - m), ci(a - s)
    print(f"| {d} | {100*a.mean():.1f} | {100*m.mean():.1f} | {100*s.mean():.1f} | {100*(a-m).mean():+.1f} ({c1[0]:+.1f}, {c1[1]:+.1f}) | {100*(a-s).mean():+.1f} ({c2[0]:+.1f}, {c2[1]:+.1f}) |")
