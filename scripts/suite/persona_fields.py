"""Personas written from outside information: do the fields survive being turned into prose?

The round-trip study showed that describing a data-learned group in prose loses most of what the group predicts, while
the same facts as a list do not. This experiment asks the same question for the descriptions most silicon-sample and
digital-twin pipelines use: a person's demographics, and their Big Five trait scores, turned into a written persona by
the model. The plainest form of that information is the raw fields, which the main study already ran as the
"demographics" and "demographics+traits" conditions on the same 1,000 records per questionnaire. The data-only ceiling
is the supervised model trained on the same fields (outputs/suite/<ds>/ceiling.json); the floor is the supervised model
given only the item id, which is the per-item most common answer.

Conditions (Gemini 3.5 Flash, thinking off, one answer per record as in the main study):
- persona_demographics: an 80-word second-person persona written by the model from the record's demographics only,
  which then replaces the demographics in the system prompt.
- persona_demographics+traits: the same from demographics plus Big Five scores, on the six questionnaires that have them.

DECISION RULES, committed before any result was computed. Paired bootstrap over records, 10,000 resamples, Holm within
each family, alpha 0.05.
- F1 (8 tests): persona_demographics minus demographics. The writing "loses" if significantly negative on at least 6 of
  8 questionnaires, "adds" if significantly positive on at least 6 of 8; otherwise the form does not matter for this
  information.
- F2 (6 tests): persona_demographics+traits minus demographics+traits, same reading.
- Context, no test: floor, ceiling for the same fields, and the three legs per questionnaire: ceiling minus floor (what
  the fields could predict), raw minus ceiling (what the model loses with the plain fields), persona minus raw (what the
  writing loses). Population level: W per item and the ratio of predicted to real spread, persona against raw."""
from __future__ import annotations
import argparse, collections, json, sys, time
from pathlib import Path
import numpy as np
from scipy.stats import wasserstein_distance
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from input_systems.suite import demographics_text, traits_text, item_prompt, parse_int
MODEL = "gemini-3.5-flash"
ALL = ["npas", "riasec", "mach", "dass", "fti", "nis", "gss2022", "wvs7"]
NAME = {"npas": "Nerdiness", "riasec": "Vocational interests", "mach": "Machiavellianism", "dass": "Distress",
        "fti": "Temperament", "nis": "Nonverbal behavior", "gss2022": "General Social Survey", "wvs7": "World Values Survey"}
DESC_SYS = "You are a researcher who writes short descriptions of survey respondents."
RAW = {"persona_demographics": "demographics", "persona_demographics+traits": "demographics+traits"}

def persona_prompt(rec, cond):
    facts = demographics_text(rec) + ("\n\n" + traits_text(rec) if "traits" in cond else "")
    return (f"Here is what is known about one respondent to an online questionnaire:\n\n{facts}\n\nWrite a description of "
            "this person, addressed to them in the second person (\"You are someone who...\"). Describe the dispositions, "
            "values, habits or tendencies you would expect of such a person. Use 3 to 5 sentences and at most 80 words. "
            "Do not copy the facts as a list.")

def build(ds, cond, client):
    recs = [json.loads(l) for l in open(f"data/suite/{ds}.jsonl")]
    if "traits" in cond and not recs[0].get("traits"): print(f"[{ds}/{cond}] skipped: no traits", flush=True); return
    t0 = time.time(); pp = Path(f"outputs/suite/{ds}/{cond}.jsonl"); out = Path(f"outputs/suite/{ds}/{MODEL}/{cond}.jsonl")
    have = {d["record_idx"]: d["text"] for d in map(json.loads, open(pp))} if pp.exists() else {}
    jobs = [i for i in range(len(recs)) if i not in have]
    rows = client.map(jobs, lambda i: {"record_idx": i, "text": client.complete(DESC_SYS, persona_prompt(recs[i], cond), sample=0).strip()})
    with open(pp, "a") as f:
        for d in rows: f.write(json.dumps(d) + "\n")
    personas = {**have, **{d["record_idx"]: d["text"] for d in rows}}
    def run(i):
        r = recs[i]; sc = r["scale"]; text = client.complete(r["base_system"] + "\n\n" + personas[i], item_prompt(r, r["target_item"]), sample=i)
        return {"record_idx": i, "subject_id": r["subject_id"], "target_item": r["target_item"], "condition": cond,
                "truth": r["items"][r["target_item"]]["answer"], "lo": sc["min"], "hi": sc["max"], "raw": text, "prediction": parse_int(text, sc["min"], sc["max"])}
    res = client.map(list(range(len(recs))), run)
    with open(out, "w") as f:
        for d in res: f.write(json.dumps(d) + "\n")
    print(f"finished {ds} {cond} ({client.calls} calls, {time.time()-t0:.0f}s)", flush=True)

def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0.0] * len(ps); run = 0.0
    for r, i in enumerate(order): run = max(run, min(1.0, (len(ps) - r) * ps[i])); adj[i] = run
    return adj

def analyze():
    rng = np.random.default_rng(0); out = {}; fam = {"F1": [], "F2": []}
    def load(ds, c):
        p = Path(f"outputs/suite/{ds}/{MODEL}/{c}.jsonl")
        return {d["record_idx"]: d for d in map(json.loads, open(p))} if p.exists() else None
    def stats(rows):
        ok = [r for r in rows if r["prediction"] is not None]
        norm = lambda v, r: 100.0 * (v - r["lo"]) / max(1, r["hi"] - r["lo"])
        t = np.array([norm(r["truth"], r) for r in ok]); p = np.array([norm(r["prediction"], r) for r in ok])
        by = collections.defaultdict(lambda: ([], []))
        for r, tt, pq in zip(ok, t, p): by[r["target_item"]][0].append(tt); by[r["target_item"]][1].append(pq)
        ws = [wasserstein_distance(a, b) for a, b in by.values() if len(a) >= 5]
        return float(np.mean(ws)), float(p.std() / t.std()) if t.std() > 0 else float("nan")
    for ds in ALL:
        ceil = json.load(open(f"outputs/suite/{ds}/ceiling.json")); out[ds] = {"floor": 100 * ceil["none"]["acc"]}
        for cond, raw in RAW.items():
            P, R = load(ds, cond), load(ds, raw)
            if not P or not R: continue
            common = sorted(set(P) & set(R))
            a_p = np.array([P[i]["prediction"] == P[i]["truth"] for i in common], float); a_r = np.array([R[i]["prediction"] == R[i]["truth"] for i in common], float)
            d = a_p - a_r; b = 100 * d[rng.integers(0, len(d), (10000, len(d)))].mean(1)
            pv = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
            Wp, sp = stats(list(P.values())); Wr, sr = stats(list(R.values()))
            out[ds][cond] = {"n": len(common), "ceiling": 100 * ceil[raw]["acc"], "raw": 100 * a_r.mean(), "persona": 100 * a_p.mean(),
                             "gain": 100 * d.mean(), "ci": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))], "p": pv,
                             "W_raw": Wr, "W_persona": Wp, "sd_raw": sr, "sd_persona": sp}
            fam["F1" if cond == "persona_demographics" else "F2"].append([ds, cond, 100 * d.mean(), *out[ds][cond]["ci"], pv])
    for cond, raw in RAW.items():
        rows = [(ds, out[ds][cond]) for ds in ALL if cond in out[ds]]
        if not rows: continue
        print(f"\n{cond} vs raw fields ({raw}); accuracy on the main study's 1,000 records (%)")
        print("| Questionnaire | Floor | Ceiling, same fields | Raw fields | Persona from fields | Ceiling − floor | Raw − ceiling | Persona − raw |\n|---|---|---|---|---|---|---|---|")
        for ds, r in rows:
            print(f"| {NAME[ds]} | {out[ds]['floor']:.1f} | {r['ceiling']:.1f} | {r['raw']:.1f} | {r['persona']:.1f} | {r['ceiling']-out[ds]['floor']:+.1f} | {r['raw']-r['ceiling']:+.1f} | {r['persona']-r['raw']:+.1f} |")
        print("\nPopulation level: W per item (lower is better) / predicted-to-real spread ratio\n| Questionnaire | Raw fields | Persona |\n|---|---|---|")
        for ds, r in rows: print(f"| {NAME[ds]} | {r['W_raw']:.1f} / {r['sd_raw']:.2f} | {r['W_persona']:.1f} / {r['sd_persona']:.2f} |")
    for f, tests in fam.items():
        if not tests: continue
        adj = holm([t[5] for t in tests]); print(f"\n{f}: persona minus raw fields\n| Questionnaire | Gain | 95% CI | Holm p |\n|---|---|---|---|")
        for t, a in zip(tests, adj): t.append(a); print(f"| {NAME[t[0]]} | {t[2]:+.1f} | {t[3]:+.1f} to {t[4]:+.1f} | {a:.4f} |")
        neg = sum(1 for t in tests if t[2] < 0 and t[6] < .05); pos = sum(1 for t in tests if t[2] > 0 and t[6] < .05)
        print(f"Significantly negative on {neg} of {len(tests)}; significantly positive on {pos} of {len(tests)}.")
    out["tests"] = fam; json.dump(out, open("outputs/persona_fields.json", "w"), indent=1, default=float)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--cond", default="persona_demographics"); ap.add_argument("--dataset", nargs="*", default=ALL)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--analyze", action="store_true"); a = ap.parse_args()
    if a.analyze: analyze()
    else:
        from input_systems.provider import GeminiClient
        client = GeminiClient(MODEL, workers=a.workers)
        for ds in a.dataset: build(ds, a.cond, client)
