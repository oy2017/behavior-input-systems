"""Build suite records for openpsychometrics datasets that include TIPI + rich demographics.
Usage: python scripts/suite/build_openpsych.py --raw-root /Users/fanyang/LLMBehavior/datasets_scan --n 1000"""
from __future__ import annotations
import argparse, csv, json, random, re, glob
from pathlib import Path

CFG = {
  "mach":   dict(dir="op_MACH",   codebook_items="json", col="{q}A", scale=(1,5), labels={1:"Disagree",2:"Slightly disagree",3:"Neutral",4:"Slightly agree",5:"Agree"}, instr="Please rate how much you agree with the following statement", domain="Machiavellianism (MACH-IV)"),
  "dass":   dict(dir="op_DASS",   codebook_items="tab",  col="{q}A", scale=(1,4), labels={1:"Did not apply to me at all",2:"Applied to me to some degree, or some of the time",3:"Applied to me to a considerable degree, or a good part of the time",4:"Applied to me very much, or most of the time"}, instr="Please indicate how much the following statement applied to you over the past week", domain="Depression Anxiety Stress Scales"),
  "npas":   dict(dir="op_NPAS",   codebook_items="tab",  col="{q}",  scale=(1,5), labels={1:"Disagree",3:"Neutral",5:"Agree"}, instr="Please rate how much you agree with the following statement", domain="Nerdy Personality Attributes Scale"),
  "riasec": dict(dir="op_RIASEC", codebook_items="tab",  col="{q}",  scale=(1,5), labels={1:"Dislike",3:"Neutral",5:"Enjoy"}, instr="Please rate how much you would like to perform the following task", domain="Holland Code (RIASEC) vocational interests"),
  "fti":    dict(dir="op_FTI",    codebook_items="json", col="{q}A", scale=(1,4), labels={1:"Strongly Disagree",2:"Disagree",3:"Agree",4:"Strongly Agree"}, instr="Please rate how much you agree with the following statement", domain="Fisher Temperament Inventory"),
  "nis":    dict(dir="op_NIS",    codebook_items="tab",  col="{q}",  scale=(1,5), labels={1:"Never",2:"Rarely",3:"Occasionally",4:"Often",5:"Very often"}, instr="Please indicate how often the following statement is true of you", domain="Nonverbal Immediacy Scale"),
}
EDU={"1":"Less than high school","2":"High school","3":"University degree","4":"Graduate degree"}
URB={"1":"Rural (country side)","2":"Suburban","3":"Urban (town, city)"}
GEN={"1":"Male","2":"Female","3":"Other"}; HAND={"1":"Right","2":"Left","3":"Both"}
REL={"1":"Agnostic","2":"Atheist","3":"Buddhist","4":"Christian (Catholic)","5":"Christian (Mormon)","6":"Christian (Protestant)","7":"Christian (Other)","8":"Hindu","9":"Jewish","10":"Muslim","11":"Sikh","12":"Other"}
ORI={"1":"Heterosexual","2":"Bisexual","3":"Homosexual","4":"Asexual","5":"Other"}
RACE={"10":"Asian","20":"Arab","30":"Black","40":"Indigenous Australian","50":"Native American","60":"White","70":"Other"}
MAR={"1":"Never married","2":"Currently married","3":"Previously married"}

def read_items(codebook: str, mode: str) -> dict:
    t = Path(codebook).read_text(encoding="utf-8", errors="replace").replace("&#39;", "'").replace("&quot;", '"')
    if mode == "json":
        body = t[t.index("{"): t.index("}") + 1]
        return {k: v for k, v in re.findall(r"""['"]((?:Q|[RIASEC])\d{1,2})['"]\s*:\s*['"](.+?)['"]\s*[,}\n]""", body)}
    return {k: v.strip() for k, v in re.findall(r"^([RIASEC]?Q?\d{1,2}|[RIASEC]\d)\t(.+?)\s*$", t, flags=re.M) if not k.startswith(("TIPI", "VCL"))}

def tipi(row):
    v = {i: int(row[f"TIPI{i}"]) for i in range(1, 11)}
    if any(x == 0 for x in v.values()): return None
    r = lambda x: 8 - x
    return {"Extraversion": (v[1] + r(v[6])) / 2, "Agreeableness": (r(v[2]) + v[7]) / 2, "Conscientiousness": (v[3] + r(v[8])) / 2,
            "Neuroticism": (v[4] + r(v[9])) / 2, "Openness": (v[5] + r(v[10])) / 2}

def demo(row):
    out = []
    def add(label, val):
        if val not in (None, "", "0"): out.append([label, val])
    add("Age", row.get("age")); add("Gender", GEN.get(row.get("gender")))
    add("Country", row.get("country")); add("Education", EDU.get(row.get("education")))
    add("Grew up in", URB.get(row.get("urban"))); add("Native English speaker", {"1": "Yes", "2": "No"}.get(row.get("engnat")))
    add("Religion", REL.get(row.get("religion"))); add("Sexual orientation", ORI.get(row.get("orientation")))
    add("Race", RACE.get(row.get("race"))); add("Voted in a national election in the past year", {"1": "Yes", "2": "No"}.get(row.get("voted")))
    add("Marital status", MAR.get(row.get("married"))); add("Number of children your mother had", row.get("familysize"))
    add("Handedness", HAND.get(row.get("hand"))); add("University major", (row.get("major") or "").strip()[:40] or None)
    return out

ap = argparse.ArgumentParser(); ap.add_argument("--raw-root", default="/Users/fanyang/LLMBehavior/datasets_scan"); ap.add_argument("--n", type=int, default=1000)
ap.add_argument("--datasets", nargs="*", default=list(CFG)); a = ap.parse_args()
rng = random.Random(0)
for name in a.datasets:
    c = CFG[name]; d = Path(a.raw_root) / c["dir"]
    csvf = glob.glob(str(d / "**/*.csv"), recursive=True)[0]; cb = glob.glob(str(d / "**/codebook*"), recursive=True)[0]
    items = read_items(cb, c["codebook_items"])
    with open(csvf, encoding="utf-8", errors="replace") as f:
        first = f.readline(); delim = "\t" if "\t" in first else ","; f.seek(0); rows = list(csv.DictReader(f, delimiter=delim))
    cols = {q: c["col"].format(q=q) for q in items}
    good = []
    for r in rows:
        try:
            ans = {q: int(float(r[col])) for q, col in cols.items()}
        except (KeyError, ValueError):
            continue
        if any(not (c["scale"][0] <= v <= c["scale"][1]) for v in ans.values()): continue
        tp = tipi(r)
        if tp is None: continue
        try: age = int(float(r["age"]))
        except: continue
        if not (13 <= age <= 90) or r.get("gender") not in ("1", "2", "3"): continue
        good.append((r, ans, tp))
    rng.shuffle(good); good = good[: a.n]
    out = Path(f"data/suite/{name}.jsonl")
    with open(out, "w") as f:
        for i, (r, ans, tp) in enumerate(good):
            tgt = rng.choice(list(ans))
            f.write(json.dumps({"dataset": name, "subject_id": f"{name}:{i}", "demographics": demo(r),
                "traits": {k: round(v, 1) for k, v in tp.items()}, "traits_note": "Your Big Five personality scores from the Ten Item Personality Inventory (each from 1 = lowest to 7 = highest):",
                "items": {q: {"text": items[q], "answer": v} for q, v in ans.items()},
                "scale": {"min": c["scale"][0], "max": c["scale"][1], "labels": {str(k): v for k, v in c["labels"].items()}, "instruction": c["instr"]},
                "target_item": tgt, "base_system": f"You are a person answering an online questionnaire ({c['domain']}).", "user_template": None}) + "\n")
    print(f"{name:7s} items={len(items):3d} complete cases={len(rows):6d}->{len(good):5d} written -> {out}")
