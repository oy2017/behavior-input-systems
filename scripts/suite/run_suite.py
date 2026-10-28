"""Run suite conditions for one dataset -> outputs/suite/<dataset>/<model>/<condition>.jsonl"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.provider import GeminiClient
from input_systems.suite import build_system, item_prompt, parse_int

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True); ap.add_argument("--model", default="gemini-3.5-flash")
ap.add_argument("--conditions", nargs="+", default=["none", "demographics", "traits", "history", "demographics+traits", "demographics+history"])
ap.add_argument("--fits", type=Path, default=None); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--limit", type=int, default=None)
a = ap.parse_args()
recs = [json.loads(l) for l in Path(f"data/suite/{a.dataset}.jsonl").read_text().splitlines()][: a.limit]
fits = {d["record_idx"]: d["type_vector"] for d in map(json.loads, a.fits.read_text().splitlines())} if a.fits else {}
brf = Path(f"data/suite_baserates/{a.dataset}.json")
if brf.exists() and any("baserate" in c for c in a.conditions):
    sys.path.insert(0, str(Path(__file__).resolve().parent)); from build_baserates import group_key  # noqa: E402
    BR = json.loads(brf.read_text())["items"]
    for r in recs:
        e = BR.get(r["target_item"])
        if e: r["_baserate"] = {"pop": e["pop"], "group": e["groups"].get(group_key(r["demographics"]))}
    if any("baserate_related" in c or "baserate_scale" in c for c in a.conditions):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        texts = {}
        for r in recs:
            for k, v in r["items"].items(): texts.setdefault(k, v["text"])
        ids = [k for k in texts if k in BR]; X = TfidfVectorizer(stop_words="english").fit_transform([texts[k] for k in ids]); sim = cosine_similarity(X)
        pos = {k: i for i, k in enumerate(ids)}
        for r in recs:
            g = group_key(r["demographics"]); tgt = r["target_item"]
            if tgt in pos:
                order = sorted((k for k in ids if k != tgt), key=lambda k: -sim[pos[tgt], pos[k]])
                rel = []
                for k in order:
                    e = BR[k]; d = (e["groups"].get(g) or {}).get("dist") or e["pop"]
                    rel.append((texts[k].split(" (")[0][:120], d))
                    if len(rel) == 5: break
                r["_baserate_related"] = rel
            # group mean answer over the questionnaire, only meaningful when all items share one scale
            scales = {(rr["scale"]["min"], rr["scale"]["max"]) for rr in recs}
            if len(scales) == 1:
                tot = n = 0.0
                for k in ids:
                    d = (BR[k]["groups"].get(g) or {}).get("dist") or BR[k]["pop"]
                    tot += sum(int(a) * p for a, p in d.items()); n += 1
                r["_baserate_scale"] = tot / n if n else None
client = GeminiClient(a.model, workers=a.workers)
for cond in a.conditions:
    if "traits" in cond and not recs[0].get("traits"): print(f"[{cond}] skipped: dataset has no traits"); continue
    out = Path(f"outputs/suite/{a.dataset}/{a.model}/{cond}.jsonl"); out.parent.mkdir(parents=True, exist_ok=True)
    jobs = [(i, r) for i, r in enumerate(recs) if "type_vector" not in cond or i in fits]
    t0 = time.time(); print(f"[{a.dataset}/{cond}] {len(jobs)} records", flush=True)
    def run(job):
        i, r = job; system = build_system(r, cond, fits.get(i)); user = item_prompt(r, r["target_item"])
        text = client.complete(system, user, sample=i); sc = r["scale"]
        return {"record_idx": i, "subject_id": r["subject_id"], "target_item": r["target_item"], "condition": cond,
                "truth": r["items"][r["target_item"]]["answer"], "lo": sc["min"], "hi": sc["max"], "raw": text, "prediction": parse_int(text, sc["min"], sc["max"])}
    with open(out, "w") as f:
        for s in range(0, len(jobs), 500):
            for d in client.map(jobs[s:s + 500], run): f.write(json.dumps(d) + "\n")
            print(f"[{a.dataset}/{cond}] {min(s+500, len(jobs))}/{len(jobs)}, {client.calls} new calls, {time.time()-t0:.0f}s", flush=True)
    print("finished", out, flush=True)
