"""Build suite records from GSS 2022 (Stata file): demographics, political identity as 'traits', ~45 ordinal attitude items."""
from __future__ import annotations
import argparse, glob, json, random
from pathlib import Path
import pandas as pd, pyreadstat
ITEMS = ["health","satfin","happy","class","finrela","natroad","natpark","natsoc","natchld","natmass","natsci","conmedic","goodlife","confinan",
         "socommun","coneduc","conarmy","socrel","socbar","socfrend","fechld","conpress","contv","conlegis","life","confed","fefam","fepresch","conjudge",
         "helppoor","helpsick","conbus","spanking","consci","wrkwayup","conclerg","premarsx","xmarsex","helpblk","conlabor","helpnot","homosex","affrmact",
         "nateduc","natenvir","natheal","natcrime","natdrug","natarms","natfare","nataid","natrace","cappun","fear","gunlaw"]
DEMO = ["age","sex","race","degree","region","income","marital","relig"]; TRAITS = ["polviews","partyid"]
ap = argparse.ArgumentParser(); ap.add_argument("--raw-root", default="/Users/fanyang/LLMBehavior/datasets_scan"); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--min-items", type=int, default=12); a = ap.parse_args()
f = glob.glob(f"{a.raw_root}/gss2022/**/*.dta", recursive=True)[0]
df, meta = pyreadstat.read_dta(f, usecols=ITEMS + DEMO + TRAITS)
lab = meta.column_names_to_labels; vl = meta.variable_value_labels
def opts(v): return {int(k): s for k, s in vl.get(v, {}).items() if isinstance(k, (int, float))}
def val(v, x):
    try: x = int(float(x))
    except: return None
    return x
rng = random.Random(0); recs = []
for _, r in df.iterrows():
    items = {}
    for v in ITEMS:
        x = val(v, r[v]); o = opts(v)
        if x is not None and x in o:
            txt = lab[v]
            if v.startswith("nat"): txt = f"Are we spending too much money, too little money, or about the right amount on: {lab[v].lower()}?"
            elif v.startswith("con"): txt = f"How much confidence do you have in the people running: {lab[v].replace('Confidence in ', '').replace('Confid. in ', '').replace('Confid in ', '').lower()}?"
            elif v.startswith("soc"): txt = f"How often do you: {lab[v].lower()}?"
            items[v] = {"text": txt, "answer": x, "options": o}
    if len(items) < a.min_items: continue
    demo = []
    for v in DEMO:
        x = r[v]
        if pd.isna(x): continue
        o = opts(v); x = int(float(x)) if v != "age" or True else x
        txt = o.get(x, str(x)) if o else str(x)
        if v == "age": txt = str(x)
        demo.append([lab[v].replace("R's ", "").replace("Respondents ", "").capitalize(), txt])
    traits = {}
    for v in TRAITS:
        x = val(v, r[v]); o = opts(v)
        if x is not None and x in o: traits[lab[v]] = o[x]
    if len(traits) < 2: continue
    recs.append((items, demo, traits))
rng.shuffle(recs); recs = recs[: a.n]
out = Path("data/suite/gss2022.jsonl")
with open(out, "w") as fo:
    for i, (items, demo, traits) in enumerate(recs):
        tgt = rng.choice(list(items)); o = items[tgt]["options"]
        # scale is item-specific in GSS: store per-record scale of the target and include options in history lines
        hist_items = {k: {"text": f"{v['text']} ({' / '.join(f'{kk}={vv}' for kk, vv in sorted(v['options'].items()))})", "answer": v["answer"]} for k, v in items.items()}
        fo.write(json.dumps({"dataset": "gss2022", "subject_id": f"gss:{i}", "demographics": demo, "traits": traits,
            "traits_note": "Your self-described political identity:", "items": hist_items,
            "scale": {"min": min(o), "max": max(o), "labels": {str(k): v for k, v in o.items()}, "instruction": "Answer the following survey question by choosing one option"},
            "target_item": tgt, "base_system": "You are a respondent in the 2022 US General Social Survey.",
            "user_template": "Answer the following survey question by choosing one option {scale}: {item}. Highlight the number of your answer in [] (such as [{lo}]). Only output your answer in brackets."}) + "\n")
print(f"gss2022: {len(recs)} records -> {out}")
