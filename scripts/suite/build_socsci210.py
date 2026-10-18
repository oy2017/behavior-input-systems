"""Build suite records from SocSci210 shards: participant-study pairs with >=2 integer-scale responses."""
from __future__ import annotations
import argparse, glob, json, random, re
from pathlib import Path
import pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument("--raw-root", default="/Users/fanyang/LLMBehavior/datasets_scan"); ap.add_argument("--n", type=int, default=1000); ap.add_argument("--out-dir", default="data/suite"); a = ap.parse_args()
rng = random.Random(0); pairs = []
for f in sorted(glob.glob(f"{a.raw_root}/socsci210/shard*.parquet")):
    df = pd.read_parquet(f, columns=["study_id", "participant", "demographic", "stimuli", "response", "task_num", "condition_num"])
    rg = df.stimuli.str.extract(r"integer from (\d+) to (\d+)")
    m = rg[0].notna(); df = df[m].copy(); df["lo"] = rg.loc[m, 0].astype(int).values; df["hi"] = rg.loc[m, 1].astype(int).values
    df = df[(df.response >= df.lo) & (df.response <= df.hi) & (df.hi - df.lo <= 10)]
    for (sid, pid), g in df.groupby(["study_id", "participant"]):
        if len(g) < 2 or g.stimuli.nunique() < 2: continue
        pairs.append((sid, pid, g))
rng.shuffle(pairs); pairs = pairs[: a.n]
out = Path(a.out_dir) / "socsci210.jsonl"
with open(out, "w") as fo:
    for i, (sid, pid, g) in enumerate(pairs):
        g = g.drop_duplicates("stimuli"); rows = list(g.itertuples())
        tgt = rng.choice(rows)
        demo = [[k.replace("_", " ").capitalize(), str(v)] for k, v in rows[0].demographic.items() if v not in (None, "", "None")]
        items = {f"s{j}": {"text": r.stimuli, "answer": int(r.response)} for j, r in enumerate(rows)}
        tgt_id = [k for k, r in zip(items, rows) if r is tgt][0]
        fo.write(json.dumps({"dataset": "socsci210", "subject_id": f"{sid}:{pid}", "study_id": sid, "demographics": demo, "traits": None, "traits_note": "",
            "items": items, "scale": {"min": int(tgt.lo), "max": int(tgt.hi), "labels": {}, "instruction": ""},
            "target_item": tgt_id, "base_system": "You are a survey respondent. Read the question below and answer exactly as this person would. Follow the response instructions precisely.",
            "user_template": "{item} Highlight your answer in [] (such as [{lo}]). Only output your answer in brackets."}) + "\n")
print(f"socsci210: {len(pairs)} records -> {out}")
