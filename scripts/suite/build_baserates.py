"""Base rates for the base-rate conditions: for each dataset and item, the answer distribution in the training pool
(population) and within demographic groups (gender x age band x education where available), excluding suite subjects.
Writes data/suite_baserates/<dataset>.json"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
def age_band(v):
    try: v = int(float(v))
    except: return "age?"
    return "age 13-20" if v <= 20 else "age 21-30" if v <= 30 else "age 31-45" if v <= 45 else "age 46+"
def group_key(demo):
    d = dict(demo); parts = []
    g = d.get("Gender") or d.get("Sex"); parts.append(str(g).lower() if g else "gender?")
    ag = d.get("Age") or d.get("Age of respondent"); parts.append(age_band(ag))
    ed = d.get("Education") or d.get("Highest degree") or d.get("Highest education level")
    if ed: parts.append(str(ed).lower()[:40])
    return " / ".join(parts)
if __name__ == "__main__":
  ap = argparse.ArgumentParser(); ap.add_argument("--datasets", nargs="+", required=True); ap.add_argument("--min-group", type=int, default=15); a = ap.parse_args()
  Path("data/suite_baserates").mkdir(exist_ok=True)
  for ds in a.datasets:
      test = [json.loads(l) for l in Path(f"data/suite/{ds}.jsonl").read_text().splitlines()]; test_ids = {r["subject_id"] for r in test}
      train = [r for r in map(json.loads, Path(f"data/suite_train/{ds}.jsonl").read_text().splitlines()) if r["subject_id"] not in test_ids]
      pop = collections.defaultdict(collections.Counter); grp = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
      for r in train:
          k = group_key(r["demographics"])
          for item, v in r["items"].items():
              pop[item][v["answer"]] += 1; grp[item][k][v["answer"]] += 1
      out = {"group_key_fields": "gender / age band / education", "items": {}}
      for item, c in pop.items():
          n = sum(c.values()); entry = {"pop": {str(k): round(v / n, 3) for k, v in sorted(c.items())}, "pop_n": n, "groups": {}}
          for k, gc in grp[item].items():
              gn = sum(gc.values())
              if gn >= a.min_group: entry["groups"][k] = {"dist": {str(kk): round(v / gn, 3) for kk, v in sorted(gc.items())}, "n": gn}
          out["items"][item] = entry
      Path(f"data/suite_baserates/{ds}.json").write_text(json.dumps(out))
      covered = sum(1 for r in test if group_key(r["demographics"]) in out["items"].get(r["target_item"], {}).get("groups", {}))
      print(f"{ds:9s} train={len(train):5d} items={len(out['items']):3d} | test records with a group base rate for their target: {covered}/{len(test)}")
