"""Cross-dataset table for the suite -> docs/suite_tables.md"""
from __future__ import annotations
import json, glob
from pathlib import Path
rows = []
for sf in sorted(glob.glob("outputs/suite/*/gemini-3.5-flash/summary.json")):
    ds = sf.split("/")[2]; S = json.load(open(sf)); cf = Path(f"outputs/suite/{ds}/ceiling.json"); C = json.load(open(cf)) if cf.exists() else {}
    rows.append((ds, S, C))
conds = ["none", "demographics", "traits", "history", "demographics+traits", "demographics+history", "type_table", "type_vector", "history+type_vector"]
L = ["# Survey suite results (generated; model = gemini-3.5-flash, thinking off; 1,000 records per dataset)\n"]
for metric, title in [("acc", "Accuracy (exact answer)"), ("W_item", "W per target item (0-100 normalised; lower is better)"), ("sd_ratio", "sd ratio (1 = human spread)")]:
    L += [f"## {title}\n", "| dataset | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
    for ds, S, C in rows:
        L.append(f"| {ds} | " + " | ".join((f"{S[c][metric]:.3f}" if metric == "acc" else f"{S[c][metric]:.2f}") if c in S else "" for c in conds) + " |")
    L.append("")
L += ["## Supervised ceiling: accuracy (pooled HistGBT trained on 4,000 to 5,000 other respondents with every item as a target; SocSci210 uses 5-fold CV on the 1,000 records)\n", "| dataset | none | demographics | traits | history | demographics+traits | demographics+history |", "|---|---|---|---|---|---|---|"]
for ds, S, C in rows:
    L.append(f"| {ds} | " + " | ".join(f"{C[c]['acc']:.3f}" if c in C else "" for c in ["none", "demographics", "traits", "history", "demographics+traits", "demographics+history"]) + " |")
Path("docs/suite_tables.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
