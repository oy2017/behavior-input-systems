"""Build suite records from WVS Wave 7 (cross-national CSV v6.0) + the public IHSN DDI codebook.
Demographics: country, sex, age, education, marital status, children, employment, social class, income step,
religion, urban/rural. Traits (measured value orientations): secular values, emancipative values, post-materialism
index, autonomy index (WVS-computed; the items feeding them are excluded from the target pool)."""
from __future__ import annotations
import argparse, json, random
from pathlib import Path
import pandas as pd, pycountry
ap = argparse.ArgumentParser(); ap.add_argument("--raw-root", default="/Users/fanyang/LLMBehavior/datasets_scan"); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--out-dir", default="data/suite"); ap.add_argument("--min-items", type=int, default=25); a = ap.parse_args()
cb = json.load(open(f"{a.raw_root}/wvs7/wvs7_codebook.json"))
# target pool: ordinal attitude/value items NOT used by the derived indices
POOL = (["Q1","Q2","Q3","Q4","Q5","Q6"] + ["Q27","Q28","Q31","Q32","Q34","Q36","Q37","Q38","Q39","Q40","Q41"] + ["Q46","Q47","Q48","Q49","Q50"]
        + ["Q57","Q58","Q59","Q60","Q61","Q62","Q63"] + ["Q64","Q65","Q66","Q67","Q68","Q72","Q73","Q74","Q75","Q76","Q77","Q78","Q79","Q80","Q81","Q82","Q83","Q84","Q85","Q86","Q87","Q88","Q89"]
        + ["Q106","Q107","Q108","Q109","Q110","Q131"] + ["Q142","Q143","Q144","Q145","Q146","Q147","Q148","Q149"] + ["Q158","Q159","Q160","Q161","Q162","Q163"]
        + ["Q183","Q186","Q187","Q188","Q189","Q190","Q191","Q192","Q193","Q194","Q195"] + ["Q199","Q235","Q236","Q237","Q238","Q239","Q240","Q250","Q252","Q253"])
DEMO = {"B_COUNTRY_ALPHA": "Country", "Q260": "Sex", "Q262": "Age", "Q275": "Highest education level", "Q273": "Marital status", "Q274": "Number of children",
        "Q279": "Employment status", "Q287": "Social class (self-described)", "Q288": "Household income step (1 = lowest tenth, 10 = highest tenth)", "Q289": "Religious denomination", "H_URBRURAL": "Lives in"}
TRAITS = {"SACSECVAL": "Secular values index (0 = traditional, 1 = secular)", "RESEMAVAL": "Emancipative values index (0 = low, 1 = high)", "Y001": "Post-materialism index (0 = materialist, 5 = post-materialist)", "Y003": "Autonomy index (-2 = obedience/faith, 2 = independence/determination)"}
usecols = POOL + list(DEMO) + list(TRAITS)
df = pd.read_csv(f"{a.raw_root}/wvs7/WVS_Cross-National_Wave_7_csv_v6_0.csv", usecols=lambda c: c in usecols, low_memory=False)
print("loaded", df.shape)
def cats(v): return {int(k): s.split("{")[0].strip() for k, s in cb.get(v, {}).get("categories", []) if k.lstrip("-").isdigit() and int(k) >= 0}
def label(v):
    l = cb.get(v, {}).get("label", v)
    for pre, new in [("Important in life: ", "How important in your life is: "), ("Confidence: ", "How much confidence do you have in: "), ("Trust: ", "How much do you trust: "),
                     ("Justifiable: ", "How justifiable is: "), ("Worries: ", "How much do you worry about: "), ("Degree of agreement: ", "Do you agree: "),
                     ("Political system: ", "How good is this way of governing the country: "), ("Science and technology: ", "Do you agree: ")]:
        if l.startswith(pre): return new + l[len(pre):]
    return l
items_meta = {}
for v in POOL:
    c = cats(v)
    if v in cb and c and len(c) >= 2:
        lo, hi = min(c), max(c)
        if hi - lo >= 1 and hi <= 10: items_meta[v] = {"text": label(v), "options": c, "lo": lo, "hi": hi}
print("items in pool with codebook:", len(items_meta))
def opt_text(m): return " / ".join(f"{k}={s}" for k, s in sorted(m["options"].items())) if len(m["options"]) <= 5 else f"{m['lo']}={m['options'][m['lo']]} ... {m['hi']}={m['options'][m['hi']]}"
def country(iso3):
    try: return pycountry.countries.get(alpha_3=iso3).name
    except Exception: return iso3
rng = random.Random(0); recs = []
for _, r in df.sample(frac=1.0, random_state=0).iterrows():
    items = {v: int(r[v]) for v, m in items_meta.items() if pd.notna(r[v]) and m["lo"] <= r[v] <= m["hi"]}
    if len(items) < a.min_items: continue
    if any(pd.isna(r[t]) or r[t] < -0.5 and t != "Y003" for t in TRAITS): continue
    demo = []
    for v, lab in DEMO.items():
        x = r[v]
        if pd.isna(x) or (isinstance(x, (int, float)) and x < 0): continue
        if v == "B_COUNTRY_ALPHA": demo.append([lab, country(str(x))]); continue
        if v in ("Q262", "Q274", "Q288"): demo.append([lab, str(int(x))]); continue
        c = cats(v)
        if v == "Q289": c = {0: "None", 1: "Roman Catholic", 2: "Protestant", 3: "Orthodox", 4: "Jewish", 5: "Muslim", 6: "Hindu", 7: "Buddhist", 8: "Other Christian", 9: "Other"}
        if int(x) not in c: continue
        demo.append([lab, c[int(x)]])
    if len(demo) < 8: continue
    traits = {lab: round(float(r[v]), 2) for v, lab in TRAITS.items()}
    recs.append((items, demo, traits))
    if len(recs) >= a.n * 3: break
rng.shuffle(recs); recs = recs[: a.n]
out = Path(a.out_dir) / "wvs7.jsonl"
with open(out, "w") as fo:
    for i, (items, demo, traits) in enumerate(recs):
        tgt = rng.choice(list(items)); m = items_meta[tgt]
        fo.write(json.dumps({"dataset": "wvs7", "subject_id": f"wvs:{i}", "demographics": demo, "traits": traits, "traits_note": "Your value-orientation scores computed from the survey:",
            "items": {v: {"text": f"{items_meta[v]['text']} ({opt_text(items_meta[v])})", "answer": ans} for v, ans in items.items()},
            "scale": {"min": m["lo"], "max": m["hi"], "labels": {str(k): s for k, s in m["options"].items()} if len(m["options"]) <= 5 else {str(m["lo"]): m["options"][m["lo"]], str(m["hi"]): m["options"][m["hi"]]}, "instruction": "Answer the following survey question"},
            "target_item": tgt, "base_system": "You are a respondent in the World Values Survey (2017-2022).",
            "user_template": "Answer the following survey question by choosing one option {scale}: {item}. Highlight the number of your answer in [] (such as [{lo}]). Only output your answer in brackets."}) + "\n")
print(f"wvs7: {len(recs)} records -> {out}")
