"""Put the BehaviorBench Big Five items into the suite record format (so the base-rate conditions can run on them),
plus a training pool of other respondents from the raw BIG5 file for base rates and ceilings."""
from __future__ import annotations
import csv, json, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.subjects import load_codebook, COLS, big_five_scores, demographics_of, DIM_NAME
RAW = "data/big5_raw/BIG5"
code = load_codebook(Path(RAW) / "codebook.txt"); item_text = {v: k for k, v in code.items()}
def cap(s): return s[0].upper() + s[1:]
SCALE = {"min": 1, "max": 5, "labels": {"1": "Disagree", "2": "Partially Disagree", "3": "Neutral", "4": "Partially Agree", "5": "Agree"}, "instruction": "Please rate how much the following statement describes you"}
def demo_pairs(d): return [["Age", str(d["age"])], ["Gender", d["gender"]], ["Country", d["country"]], ["Race", d["race"]], ["Handedness", d["handedness"]], ["Native English speaker", "Yes" if d["native_english"] else "No"]]
def rec(sid, demo, answers, tgt):
    return {"dataset": "bigfive", "subject_id": sid, "demographics": demo, "traits": {DIM_NAME[k[0]] if len(k)==1 else k: v for k, v in big_five_scores(answers).items()},
            "traits_note": "Your Big Five personality test scores (each from 10 = lowest to 50 = highest):",
            "items": {c: {"text": cap(item_text[c]), "answer": v} for c, v in answers.items()}, "scale": SCALE, "target_item": tgt,
            "base_system": "You are a person answering a personality survey.", "user_template": None}
# suite records = the 997 Track A records
ta = [json.loads(l) for l in Path("data/track_a_subjects.jsonl").read_text().splitlines()]
Path("data/suite").mkdir(exist_ok=True); Path("data/suite_train").mkdir(exist_ok=True)
with open("data/suite/bigfive.jsonl", "w") as f:
    for r in ta:
        f.write(json.dumps(rec(f"bigfive:{r['raw_row']}", demo_pairs(demographics_of({k: str(v) for k, v in r["demographics"].items()})), r["answers"], r["target_item"])) + "\n")
used = {r["raw_row"] for r in ta}
with open(Path(RAW) / "data.csv", encoding="utf-8", errors="replace") as f: raw = list(csv.DictReader(f, delimiter="\t"))
rng = random.Random(0); idx = [i for i in range(len(raw)) if i not in used]; rng.shuffle(idx); n = 0
with open("data/suite_train/bigfive.jsonl", "w") as f:
    for i in idx:
        r = raw[i]
        try: answers = {c: int(r[c]) for c in COLS}; age = int(r["age"])
        except ValueError: continue
        if any(v < 1 or v > 5 for v in answers.values()) or not (13 <= age <= 90): continue
        f.write(json.dumps(rec(f"bigfive:{i}", demo_pairs(demographics_of(r)), answers, rng.choice(COLS))) + "\n"); n += 1
        if n >= 6000: break
print(f"bigfive suite records: {len(ta)}; training pool: {n}")
