# behavior-input-systems

How does the **input system** — what we tell a language model about a person —
change how well the model predicts that person's behavior?

Project with Jin Huang and Prof. Qiaozhu Mei (Foreseer lab, UMich). Proposed
in Slack on 2026-09-21: compare demographics vs. Big Five personality vs.
behavior codes / type vectors as model inputs, using BehaviorBench as the
first dataset.

Full proposal with literature grounding: [docs/PROPOSAL.md](docs/PROPOSAL.md). Data and model feasibility check: [docs/DATA_FEASIBILITY.md](docs/DATA_FEASIBILITY.md).

First model: `gemini-3.5-flash` with thinking off (`reasoning_effort: "none"`); key in `.env` as `GEMINI_API_KEY`.

## Research question

For the same target subjects and the same prediction tasks, hold the model
fixed and vary only the description of the subject. Measure prediction
quality at the individual level (error per subject) and the distribution
level (Wasserstein distance between predicted and human response
distributions), exactly as BehaviorBench does.

## Input systems (conditions)

| Condition | What the model is told about the subject | Source |
| --- | --- | --- |
| `none` | Nothing. Population prior. | — |
| `demographics` | Age, gender, country, race, native language, handedness. | Big Five raw data |
| `big_five` | Five OCEAN scores (10–50). | Big Five raw data |
| `play_history` | Observed choices in other economic games (raw behavior). | MobLab `acrossgame` |
| `type_vector` | Trait intensities (Risk Aversion, Strategic Sophistication, Trust, 1–5) fitted to the subject's other-game choices, per Jackson, Manning, Xie, Yuan & Mei (2026). | fitted from MobLab |
| `demographics+big_five`, `play_history+type_vector` | Combinations. | — |

## Two tracks

**Track A — Big Five subset.** Same 1,000 participants as BehaviorBench's
`surv_resp_pred` / `pers_score_pred` tasks (recoverable via
`behaviorbench_indices.json` against the public Kaggle OCEAN file). Targets:
survey item responses and held-out personality dimensions. Conditions:
`none`, `demographics`, `big_five`, `demographics+big_five`.

**Track B — MobLab subset.** Same subjects as BehaviorBench's
`acrossgame_behavior` tasks (`metadata.user_id`, 750 per target game).
Target: first-round choice in the target game. Conditions: `none`,
`play_history` (the existing BehaviorBench prompt), `type_vector`,
`play_history+type_vector`.

Type vectors are fitted cheaply: with a crafted system prompt the model is
near-deterministic (see the KDD reproduction, finding 3), so we precompute a
lookup table of 5×5×5 = 125 type vectors × 9 game roles per model (~1,125
calls), then fit each subject by nearest match on their history games.

## Metrics

Reuse `behaviorbench` (the evaluation package) for parsing and scoring:
individual error (MAE / accuracy) and distribution distance (Wasserstein).
Report both per condition, per task, per model.

## Models

Start with what is already available: Gemini (free quota), GLM-5.2 and
Tencent HY3 via OpenRouter, and GPT-4o-mini for comparability with the KDD
paper. Add one strong model later.

## Phases

1. **Scaffold (this week).** Subject table, prompt builders, dummy run.
2. **Track A.** 4 conditions × 2 tasks × 2 models, n = 1,000.
3. **Track B.** Type-vector lookup table, fit, 4 conditions × 7 games × 2 models.
4. **Analysis + write-up.** Which input system helps which task, and whether
   gains are individual-level, distribution-level, or both.

## Layout

```
src/input_systems/
  conditions.py    # input-system prompt builders (the experimental conditions)
  subjects.py      # matched subject tables for Track A and Track B
  type_vector.py   # type-vector lookup table and per-subject fit
scripts/run_track.py
data/      # not committed: Kaggle OCEAN data.csv, BehaviorBench bundle, joint.csv
outputs/   # not committed: model outputs and scores
docs/      # plan, update drafts
```

## Setup

```bash
uv sync
# BehaviorBench evaluation data (public)
git clone https://huggingface.co/datasets/befm/BehaviorBench data/behaviorbench
# Big Five raw file (same data as the Kaggle file BehaviorBench cites; no login needed)
mkdir -p data/big5_raw && curl -L -o data/big5_raw/BIG5.zip https://openpsychometrics.org/_rawdata/BIG5.zip && unzip -q data/big5_raw/BIG5.zip -d data/big5_raw
# MobLab joint table (same participant across games):
curl -L -o data/joint.csv https://raw.githubusercontent.com/oy2017/prompt-mixture-alignment/main/data/joint.csv
```

## Related work in this lab

- BehaviorBench (arXiv 2606.24162) — tasks, data, metrics.
- Distributional Alignment via Mixture Modeling (Xie, Gao, Mei, KDD 2026) — reproduced in `oy2017/prompt-mixture-alignment`.
- Modeling Human Behavior with Type Vectors (Jackson et al., arXiv 2608.18265) — the behavior-code input.
- Categorizing Strategic Situations (Xie, Mei, Yuan, Jackson, PNAS 2025).
