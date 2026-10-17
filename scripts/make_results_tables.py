"""Regenerate docs/results_tables.md from outputs/*/summary.json and ceiling.json."""
import json
from pathlib import Path
A = json.load(open("outputs/track_a/gemini-3.5-flash/summary.json")); Ac = json.load(open("outputs/track_a/ceiling.json"))
B = json.load(open("outputs/track_b/gemini-3.5-flash/summary.json")); Bc = json.load(open("outputs/track_b/ceiling.json"))
L = ["# Result tables (generated; model = gemini-3.5-flash, thinking off)\n"]
L += ["## Track A: survey item prediction, 997 matched subject-item pairs\n", "| Condition | LLM acc | LLM MAE | LLM W(item) | sd ratio | Supervised ceiling acc | Ceiling W(item) |", "|---|---|---|---|---|---|---|"]
for c in ["none", "demographics", "big_five", "demographics+big_five", "history", "demographics+history"]:
    a = A.get(c); ce = Ac.get(c)
    ce_acc = f"{ce['acc']:.3f}" if ce else "(per-item mode 0.313)"; ce_w = f"{ce['W_item']:.3f}" if ce else "-"
    L.append(f"| {c} | {a['acc']:.3f} | {a['mae']:.3f} | {a['W_item']:.3f} | {a['sd_ratio']:.2f} | {ce_acc} | {ce_w} |")
L += ["", "## Track B: held-out game prediction, 6,262 records, per game\n"]
conds = sorted({k.split("|")[1] for k in B})
order = [c for c in ["none", "history", "type_table", "type_vector", "history+type_vector"] if c in conds]
L += ["| Game | n | " + " | ".join(f"{c} MAE / W" for c in order) + " | HistGBT MAE | W floor |", "|---|---|" + "---|" * len(order) + "---|---|"]
for g in ["dictator", "ultimatum_proposer", "ultimatum_responder", "trust_investor", "trust_banker", "public_goods", "bomb", "guessing"]:
    cells = []
    for c in order:
        v = B.get(f"{g}|{c}"); cells.append(f"{v['mae']:.1f} / {v['W']:.1f}" if v else "")
    L.append(f"| {g} | {B[f'{g}|none']['n']} | " + " | ".join(cells) + f" | {Bc[g]['histgbt_mae']:.1f} | {Bc[g]['W_floor']:.2f} |")
cells = []
for c in order:
    v = B.get(f"push_pull|{c}"); cells.append(f"acc {v['acc']:.3f}" if v else "")
L.append("| push_pull (categorical) | 750 | " + " | ".join(cells) + " | - | - |")
L += ["", "### Track B means over the eight numeric games\n", "| Condition | MAE | W | mean sd ratio |", "|---|---|---|---|"]
import statistics
for c in order:
    vs = [B[f"{g}|{c}"] for g in ["dictator", "ultimatum_proposer", "ultimatum_responder", "trust_investor", "trust_banker", "public_goods", "bomb", "guessing"] if f"{g}|{c}" in B]
    L.append(f"| {c} | {statistics.mean(v['mae'] for v in vs):.2f} | {statistics.mean(v['W'] for v in vs):.2f} | {statistics.mean(v['sd_ratio'] for v in vs):.2f} |")
L.append(f"| HistGBT ceiling | {statistics.mean(Bc[g]['histgbt_mae'] for g in Bc):.2f} | - | - |")
Path("docs/results_tables.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
