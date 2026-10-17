"""Type-vector fitting (Jackson, Manning, Xie, Yuan & Mei, 2026), done as a lookup.

1. build_table(): for every type vector in {1..5}^3 and every game role, ask the
   model (with the type-vector system prompt) for its choice. ~1,125 calls per
   model. Cached to outputs/type_vector_table_<model>.json.
2. fit_subject(): choose the type vector whose table row is closest (L1 over
   the subject's *history* games only) to the subject's observed choices.
   The target game is never used for fitting.

The model's answer under a crafted system prompt is near-deterministic (KDD
reproduction, finding 3), so one call per (vector, game) is enough to start;
raise `samples` if a model turns out to be noisy.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from .conditions import TYPE_VECTOR_TRAITS, type_vector

GAME_ROLES = ("dictator", "ultimatum_proposer", "ultimatum_responder", "trust_investor",
              "trust_banker", "public_goods", "bomb", "guessing", "push_pull")

ALL_VECTORS = [dict(zip(TYPE_VECTOR_TRAITS, v)) for v in itertools.product(range(1, 6), repeat=3)]


def build_table(model_call, game_prompts: dict[str, str], cache: Path, samples: int = 1) -> dict:
    """model_call(system, user) -> parsed numeric choice. game_prompts: role -> user prompt."""
    table = json.loads(cache.read_text()) if cache.exists() else {}
    for tv in ALL_VECTORS:
        key = json.dumps(tv, sort_keys=True)
        row = table.setdefault(key, {})
        for role, prompt in game_prompts.items():
            if role in row:
                continue
            vals = [model_call(type_vector({"type_vector": tv}), prompt) for _ in range(samples)]
            row[role] = sum(vals) / len(vals)
            cache.write_text(json.dumps(table, indent=1))
    return table


def fit_subject(table: dict, observed: dict[str, float]) -> dict[str, int]:
    """observed: role -> the subject's actual choice, history games only."""
    best, best_d = None, float("inf")
    for key, row in table.items():
        d = sum(abs(row[r] - v) for r, v in observed.items() if r in row)
        if d < best_d:
            best, best_d = key, d
    return json.loads(best)
