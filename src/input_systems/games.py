"""Canonical MobLab game prompts (from the BehaviorBench records), action ranges, and answer parsing."""

from __future__ import annotations

import collections
import json
import re
from pathlib import Path

ROLES = ["dictator", "ultimatum_proposer", "ultimatum_responder", "trust_investor", "trust_banker",
         "public_goods", "bomb", "guessing", "push_pull"]
LABEL2ROLE = {"The Dictator Game": "dictator", "The Ultimatum Game (as the Proposer)": "ultimatum_proposer",
              "The Ultimatum Game (as the Responder)": "ultimatum_responder",
              "The Trust Game (as the Investor)": "trust_investor", "The Trust Game (as the Banker)": "trust_banker",
              "The Public Goods Game": "public_goods", "The Bomb Risk Game": "bomb",
              "The Beauty Contest Game": "guessing"}
RANGE = {"dictator": (0, 100), "ultimatum_proposer": (0, 100), "ultimatum_responder": (0, 100),
         "trust_investor": (0, 100), "trust_banker": (0, 150), "public_goods": (0, 20), "bomb": (0, 100),
         "guessing": (0, 100), "push_pull": None}
GAME_SYSTEM = "You are a player who is playing an economics game."


def canonical_prompts(track_b_jsonl: Path) -> dict[str, str]:
    """Most common instruction text per role across target and history occurrences."""
    cnt = collections.defaultdict(collections.Counter)
    for line in Path(track_b_jsonl).read_text().splitlines():
        r = json.loads(line)
        cnt[r["target_game"]][target_instruction(r["record"]["user"])] += 1
        for h in r["history"]:
            cnt[LABEL2ROLE[h["label"]]][h["instruction"]] += 1
    return {role: cnt[role].most_common(1)[0][0] for role in ROLES if cnt[role]}


def target_instruction(user_prompt: str) -> str:
    return user_prompt.split("game instruction below:\n\n", 1)[1].strip() if "game instruction below:" in user_prompt else user_prompt.strip()


def parse_answer(text: str, role: str):
    """Numeric choice (float) or 'Push'/'Pull'; None if unparseable."""
    if role == "push_pull":
        m = re.findall(r"\[(Push|Pull)\]", text, flags=re.I)
        return m[-1].capitalize() if m else None
    m = re.findall(r"\[\s*\$?\s*(-?\d+(?:\.\d+)?)\s*(?:%|dollars?)?\s*\]", text)
    if not m:
        return None
    v = float(m[-1]); lo, hi = RANGE[role]
    return v if lo <= v <= hi else None


def normalize(v: float, role: str) -> float:
    lo, hi = RANGE[role]
    return 100.0 * (v - lo) / (hi - lo)
