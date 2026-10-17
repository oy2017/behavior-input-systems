"""Track A main run: conditions x matched Big Five records -> outputs/track_a/<model>/<condition>.jsonl

All conditions use BehaviorBench's first-person Demo-to-Resp framing; only the subject description varies.
  none, demographics, big_five, history (the other 49 answers), demographics+big_five, demographics+history
"""
from __future__ import annotations
import argparse, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_systems.provider import GeminiClient
from input_systems.subjects import load_codebook, COLS, DIM_NAME, GENDER, HAND, RACE

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--conditions", nargs="+", default=["none", "demographics", "big_five", "history", "demographics+big_five", "demographics+history"])
ap.add_argument("--workers", type=int, default=8); ap.add_argument("--limit", type=int, default=None)
ap.add_argument("--fits", type=Path, default=None, help="fits_<traits>.jsonl; enables conditions type_vector and history+type_vector")
ap.add_argument("--levels", type=int, default=3)
a = ap.parse_args()
code = load_codebook(Path("data/big5_raw/BIG5/codebook.txt")); item_text = {v: k for k, v in code.items()}
recs = [json.loads(l) for l in Path("data/track_a_subjects.jsonl").read_text().splitlines()][: a.limit]
client = GeminiClient(a.model, workers=a.workers)
fits = {d["record_idx"]: d["type_vector"] for d in map(json.loads, a.fits.read_text().splitlines())} if a.fits else {}
def type_text(tv):
    return (f"You are characterized by the following profile (each dimension is measured on a Likert scale, where 1 is the lowest level and {a.levels} is the highest).\n" + "\n".join(f"- {t}: {v} out of {a.levels}" for t, v in tv.items()))
ITEM = ("The following item was rated on a five-point scale where 1=Disagree, 2=Partially Disagree, 3=Neutral, "
        "4=Partially Agree, 5=Agree. Please select how this statement describes you and highlight your answer in []"
        "(such as [1],[2],[3],[4],or [5]): {item} Only output your answer in brackets.")

def cap(s): return s[0].upper() + s[1:]
def demo_text(d):
    eng = "is English" if d["engnat"] == "1" else "is not English"
    return (f"You are a {d['age']}-year-old {GENDER.get(d['gender'],'person')} from {d['country']}. You are {HAND.get(d['hand'],'Right-handed')}. "
            f"Your race is {RACE.get(d['race'],'Other')}. Your native language {eng}.")
def big5_text(s):
    return ("Your Big Five personality test scores (each from 10 = lowest to 50 = highest) are:\n" +
            "\n".join(f"- {DIM_NAME.get(k, k)}: {v}" for k, v in s.items()))
def hist_text(ans, target):
    lines = [f"- {cap(item_text[c])} Answer: [{v}]" for c, v in ans.items() if c != target]
    return ("You previously answered the following items of a personality test on the same five-point scale:\n" + "\n".join(lines))

def build(rec, cond, i=None):
    parts = ["You are a person answering a personality survey."]
    if "type_vector" in cond: parts.append(type_text(fits[i]))
    if "demographics" in cond: parts.append(demo_text(rec["demographics"]))
    if "big_five" in cond: parts.append(big5_text(rec["big_five"]))
    if "history" in cond: parts.append(hist_text(rec["answers"], rec["target_item"]))
    return "\n\n".join(parts), ITEM.format(item=cap(item_text[rec["target_item"]]))

for cond in a.conditions:
    suffix = f"_{a.fits.stem.split('_', 1)[1]}" if ("type_vector" in cond and a.fits) else ""
    out = Path(f"outputs/track_a/{a.model}/{cond}{suffix}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time(); print(f"[{cond}] {len(recs)} records", flush=True)
    def run(job):
        i, rec = job; system, user = build(rec, cond, i)
        text = client.complete(system, user, sample=i)
        m = re.findall(r"\[([1-5])\]", text)
        return {"record_idx": i, "subject_id": rec.get("subject_id", rec.get("raw_row")), "target_item": rec["target_item"], "condition": cond,
                "truth": rec["target_answer"], "raw": text, "prediction": int(m[-1]) if m else None}
    with open(out, "w") as f:
        for s in range(0, len(recs), 500):
            for d in client.map(list(enumerate(recs))[s:s + 500], run):
                f.write(json.dumps(d) + "\n")
            print(f"[{cond}] {min(s+500, len(recs))}/{len(recs)}, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
    print("finished", out, flush=True)
