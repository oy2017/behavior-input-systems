"""Generic survey-suite: one record format for many datasets, one prompt builder, one scorer.

Record (JSONL):
  {"dataset", "subject_id", "demographics": [[label, value], ...], "traits": {name: value} | null,
   "traits_note": str, "items": {item_id: {"text": str, "answer": int}}, "scale": {"min": int, "max": int,
   "labels": {str(int): str}, "instruction": str}, "target_item": item_id, "base_system": str,
   "user_template": str | null}
Conditions: none, demographics, traits, history, demographics+traits, demographics+history,
            type_vector (needs fits), history+type_vector.
"""
from __future__ import annotations
import re

TRAITS_BF3 = ["Extraversion", "Agreeableness", "Neuroticism"]


def scale_text(scale: dict) -> str:
    labs = ", ".join(f"{k}={v}" for k, v in sorted(scale["labels"].items(), key=lambda kv: int(kv[0])))
    return f"on a scale from {scale['min']} to {scale['max']} ({labs})"


def item_prompt(rec: dict, item_id: str) -> str:
    it = rec["items"][item_id]; sc = rec["scale"]
    if rec.get("user_template"):
        return rec["user_template"].format(item=it["text"], lo=sc["min"], hi=sc["max"], scale=scale_text(sc))
    return (f"{sc.get('instruction', 'Please rate the following statement')} {scale_text(sc)}: {it['text']} "
            f"Highlight your answer in [] (such as [{sc['min']}] or [{sc['max']}]). Only output your answer in brackets.")


def demographics_text(rec: dict) -> str:
    return "Your profile:\n" + "\n".join(f"- {k}: {v}" for k, v in rec["demographics"])


def traits_text(rec: dict) -> str:
    return rec.get("traits_note", "Your trait scores:") + "\n" + "\n".join(f"- {k}: {v}" for k, v in rec["traits"].items())


def history_text(rec: dict) -> str:
    sc = rec["scale"]; tgt = rec["target_item"]
    lines = [f"- {v['text']} Answer: [{v['answer']}]" for k, v in rec["items"].items() if k != tgt]
    return f"You previously answered the following items {scale_text(sc)}:\n" + "\n".join(lines)


def type_text(tv: dict, levels: int = 3) -> str:
    return (f"You are characterized by the following profile (each dimension is measured on a Likert scale, "
            f"where 1 is the lowest level and {levels} is the highest).\n" + "\n".join(f"- {t}: {v} out of {levels}" for t, v in tv.items()))


def baserate_text(rec: dict, cond: str) -> str:
    """Population answer shares for the target item (`baserate`), or the shares within the person's demographic
    group (`demographics+baserate`; falls back to the population when the group is too small)."""
    br = rec.get("_baserate") or {}
    if not br: return ""
    if "demographics" in cond and br.get("group"):
        g = br["group"]
        return (f"For reference, among {g['n']} other respondents with your gender, age range, and education, "
                f"the answers to this question were distributed as: " + ", ".join(f"{k}: {round(100*v)}%" for k, v in g["dist"].items()) + ".")
    return ("For reference, across all other respondents the answers to this question were distributed as: "
            + ", ".join(f"{k}: {round(100*v)}%" for k, v in br["pop"].items()) + ".")


def build_system(rec: dict, cond: str, tv: dict | None = None) -> str:
    parts = [rec["base_system"]]
    if "demographics" in cond: parts.append(demographics_text(rec))
    if "baserate" in cond: parts.append(baserate_text(rec, cond))
    if "traits" in cond and rec.get("traits"): parts.append(traits_text(rec))
    if "type_vector" in cond and tv: parts.append(type_text(tv))
    if "history" in cond: parts.append(history_text(rec))
    return "\n\n".join(parts)


def parse_int(text: str, lo: int, hi: int):
    m = re.findall(r"\[\s*(-?\d+)\s*\]", text)
    if not m: return None
    v = int(m[-1]); return v if lo <= v <= hi else None
