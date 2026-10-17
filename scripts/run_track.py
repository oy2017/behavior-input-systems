"""Run one track: conditions x tasks x models -> BehaviorBench-format outputs.

    uv run python scripts/run_track.py --track A --model gemini-2.5-flash --num-samples 50

Skeleton: wires conditions.py + subjects.py to a provider call and writes JSONL
that behaviorbench's scorer can read. Provider/scorer hookup is Phase 1.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from input_systems.conditions import TRACK_A, TRACK_B, build_system_prompt

TRACK_TASKS = {
    "A": ["surv_resp_pred", "pers_score_pred"],
    "B": ["acrossgame_behavior_" + g for g in
          ("dictator", "ultimatum_proposer", "trust_investor", "public_goods", "bomb", "guessing", "push_pull")],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=["A", "B"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--conditions", nargs="*")
    ap.add_argument("--num-samples", type=int, default=None)
    ap.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = ap.parse_args()

    conds = args.conditions or (TRACK_A if args.track == "A" else TRACK_B)
    for task in TRACK_TASKS[args.track]:
        for cond in conds:
            out = args.output_dir / args.model / task / f"{cond}.jsonl"
            out.parent.mkdir(parents=True, exist_ok=True)
            # TODO Phase 1: load subjects + records, build_system_prompt(...), call provider,
            # write {"system","user","assistant","prediction","metadata"} per line, then score
            # with behaviorbench.eval metrics.
            print(f"[plan] {task:32s} {cond:26s} -> {out}")


if __name__ == "__main__":
    main()
