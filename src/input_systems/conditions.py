"""Experimental conditions: how a subject is described to the model.

Each condition is a function (subject -> system-prompt text). The task prompt
(the `user` field of a BehaviorBench record) is left unchanged, so the only
thing that varies across conditions is the subject description.

A `subject` is a plain dict produced by `subjects.py`; keys are optional and a
condition raises KeyError if it needs one that is missing.
"""

from __future__ import annotations

from typing import Callable

Subject = dict
Condition = Callable[[Subject], str]

BIG_FIVE_DIMS = ("Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness")
TYPE_VECTOR_TRAITS = ("Risk Aversion", "Strategic Sophistication", "Trust")


def none(subject: Subject) -> str:
    return ""


def demographics(subject: Subject) -> str:
    """Mirror BehaviorBench's own demographic framing (surv_resp_pred system prompt)."""
    d = subject["demographics"]
    eng = "is English" if d.get("native_english") else "is not English"
    return (
        f"You are a {d['age']}-year-old {d['gender']} from {d['country']}. "
        f"You are {d['handedness']}. Your race is {d['race']}. "
        f"Your native language {eng}."
    )


def big_five(subject: Subject, dims: tuple[str, ...] = BIG_FIVE_DIMS) -> str:
    """Five OCEAN scores on the 10-50 scale used by BehaviorBench."""
    s = subject["big_five"]
    lines = "\n".join(f"* {dim}: {s[dim]}" for dim in dims if dim in s)
    return (
        "Your Big Five personality test scores (each from 10 = lowest to 50 = highest):\n"
        f"{lines}"
    )


def play_history(subject: Subject) -> str:
    """Raw observed choices in other games, in BehaviorBench's acrossgame format."""
    hist = subject["play_history"]  # list of {game_label, instruction, choice}
    blocks = []
    for i, h in enumerate(hist, 1):
        blocks.append(
            f"{i}. {h['game_label']}\n"
            f"- Game instruction: {h['instruction']}\n"
            f"- Your choice: [{h['choice']}]"
        )
    return "## Play History\nYou have played the following economics games before.\n\n" + "\n\n".join(blocks)


def type_vector(subject: Subject) -> str:
    """Type-vector framing, exact format of Jackson, Manning, Xie, Yuan & Mei (2026), Figure 1."""
    tv = subject["type_vector"]  # dict trait -> int in 1..5
    bullets = "\n".join(f"- {t}: {tv[t]} out of 5" for t in TYPE_VECTOR_TRAITS if t in tv)
    return ("You are a player characterized by the following profile (each dimension is measured on a "
            "Likert scale, where 1 is the lowest level and 5 is the highest).\n" + bullets)


def combine(*conds: Condition) -> Condition:
    def _c(subject: Subject) -> str:
        return "\n\n".join(t for t in (c(subject) for c in conds) if t)
    return _c


CONDITIONS: dict[str, Condition] = {
    "none": none,
    "demographics": demographics,
    "big_five": big_five,
    "play_history": play_history,
    "type_vector": type_vector,
    "demographics+big_five": combine(demographics, big_five),
    "play_history+type_vector": combine(play_history, type_vector),
}

TRACK_A = ("none", "demographics", "big_five", "demographics+big_five")
TRACK_B = ("none", "play_history", "type_vector", "play_history+type_vector")


def build_system_prompt(task_system: str, condition: str, subject: Subject) -> str:
    """Prepend the task's own framing (e.g. 'You are an expert in psychology...')
    to the subject description for the chosen condition."""
    desc = CONDITIONS[condition](subject)
    return f"{task_system}\n\n{desc}".strip() if desc else task_system
