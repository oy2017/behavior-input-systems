# Research proposal: Which input system should a behavior model be given?

Owen Yang, with Jin Huang and Prof. Qiaozhu Mei (Foreseer lab). Draft v1, 2026-10-16.

## 1. The problem

BehaviorBench frames human behavior as p(y | x, c; K): behavior y given the
subject's characteristics x, the context c, and knowledge K. Every behavior
model in the literature fixes x to one representation and never asks whether
it is the right one:

| Work | What the model is told about the person (x) | Level evaluated |
| --- | --- | --- |
| BehaviorBench, SubPOP, Socrates, SocSci210 | Demographics (age, gender, race, country ...) | Individual + distributional |
| BehaviorBench Seq./Masked tasks, Psych-101, Centaur | The person's own prior responses or actions | Individual |
| OdysSim | A free-text prose persona written by an LLM | Mostly population; weak on individual tasks |
| Xie, Gao & Mei (KDD 2026); Xie et al. (PNAS 2025) | A *learned* latent prompt, tied to no real person | Distributional only; "we do not attempt individual-level identification" |
| Jackson, Manning, Xie, Yuan & Mei (2026) | A fitted low-dimensional **type vector** (e.g. Risk Aversion 2/5, Strategic Sophistication 4/5, Trust 3/5) | Individual match + held-out-game prediction; distribution match |
| Ziems et al. (2026) | One fixed scheme per task (demographics for WVS, history for Psych-101) | No ablation of input richness |

Three facts from these papers make the choice of x the open problem:

1. **Demographics are a weak x.** The KDD paper's demographic-persona baseline
   (OASIS) is among the worst distributionally (W 5.3 to 10.2 vs 0.4 to 1.5 for
   learned prompts) because "individuals sharing the same demographic profile
   can behave very differently." On BehaviorBench the best model reaches only
   32.4% accuracy predicting a survey item from demographics, versus 43.1% from
   prior items and 49.0% from the other 49 items.
2. **Individual and distributional performance disagree.** Frontier models
   predict the population mean well but reproduce only 0.53 to 0.70 of the
   human standard deviation; behavior foundation models preserve diversity but
   lag at individual prediction. Fine-tuning improved distributional metrics by
   46 to 63% but individual metrics by only 4 to 12%, which the authors
   attribute to the individual task needing p(y | x, c) rather than p(y | c).
   So the bottleneck for individual-level accuracy is x, not more behavioral
   training data.
3. **A three-dimensional type vector already rivals a supervised ML model.** Fitting
   (Risk Aversion, Strategic Sophistication, Trust) on a subject's other games
   and applying it to a held-out game gives error 1.11x a HistGBT model trained
   in-distribution on that game, vs 1.43x for a random human and 1.73x for a
   uniform guess. Economic traits beat Big Five trait names as type dimensions
   from k=2 upward. Yet this was never compared against demographics or raw
   history as inputs, never run on a benchmark, and never scored on W.

The scaling paper adds the motivation: "individual idiosyncrasies" are one of
the failure modes that do not improve with pre-training compute, so the input
representation is where individual-level gains have to come from.

**Research question.** Holding the model, the task, and the subjects fixed,
how does the input system x change behavior prediction at the individual and
the distributional level, and is there an x that is good at both?

## 2. Input systems to compare

We organise x along two axes: *where the information comes from* (exogenous
attributes, self-reported traits, observed behavior) and *how compressed it is*
(number of values handed to the model).

| Condition | What the model gets | Source | Size |
| --- | --- | --- | --- |
| `none` | nothing (population prior) | — | 0 |
| `demographics` | age, gender, country, race, native language, handedness | self-report | 6 fields |
| `big_five` | the five OCEAN scores (10 to 50) | self-report, scored | 5 numbers |
| `history` | the person's own observed choices (other games / other survey items) | behavior | 1 to 49 values |
| `type_vector` | (R, S, T) on 1 to 5 fitted to the person's *other* observations through the LLM, exactly as in Jackson et al. | behavior, fitted | 3 numbers |
| combinations | `demographics+big_five`, `history+type_vector`, `demographics+history` | | |

`type_vector` is the "behavior code" input. The PNAS
behavioral codes are free-text motivation prompts tied to a behavior, not a
person, so the person-level version is the Jackson et al. type vector; we
follow its prompt format and its leave-one-game-out fitting rule (the target
observation is never used to fit).

## 3. Data

BehaviorBench (Hugging Face `befm/BehaviorBench`) plus its two public upstream
sources, so that each subject can be described in several ways.

**Track A: survey behavior (Big Five source).** The 1,000 subjects behind the
Demo-to-Resp task. The Kaggle OCEAN file gives each subject demographics *and*
50 item responses, so from `behaviorbench_indices.json` we can rebuild, for the
same person and the same target item: demographics, Big Five scores, the other
49 responses (history), and a type vector fitted on those 49 responses.
Target: the held-out item (5-point Likert). Metrics: accuracy and MAE
(individual), W over the item's response distribution (distributional).

**Track B: game behavior (MobLab source).** The 750 subjects per target game
behind the Across-Ctx task (`metadata.user_id`), with their first-round choices
in the other games from the joint table in `prompt-mixture-alignment/data/joint.csv`.
Conditions: `none`, `history` (the existing Across-Ctx prompt), `type_vector`,
`history+type_vector`. Target: first-round choice in the target game, 7 games.
Metrics: MAE on the 0 to 100 normalised range, W per game, bootstrap lower
bound on W as in BehaviorBench.

Demographics are not in the BehaviorBench MobLab release ("MobLab lacks
sufficient demographic attributes", KDD paper); if the lab's raw MobLab
export has country, Track B gets a `demographics` arm. Ask Jin.

Limitation stated up front: no subject has both personality and game data, so
cross-domain transfer of a type vector (games to surveys) is out of scope for
this phase.

## 4. Models

Fix inference settings to each lab paper's convention: default sampling
parameters, non-reasoning models, system prompt = subject description, user
prompt = unchanged BehaviorBench task prompt.

| Model | Why |
| --- | --- |
| GPT-4.1 | Backbone of the type-vector paper; strongest non-reasoning GPT on BehaviorBench; its type-vector choices can be checked against the paper's Figure 2 |
| Gemini 3.1 Flash (Pro if budget allows) | Free quota; Pro is #1 distributionally on BehaviorBench |
| GLM-5.2 | Open-weight, already on the leaderboard (our PR), top-5 at both levels |
| One behavior foundation model: BehaviorBench's fine-tuned Qwen3-4B or Be.FM-1.5-4B (weights from the lab) | Tests whether a model trained on behavior data uses x differently (H5) |

Three general-purpose models plus one behavior foundation model is enough for
the main claims; more can be added through the existing OpenRouter path.

## 5. Experiments and the questions they answer

**E1. Main comparison (both tracks).** Full factorial of condition x model on
the fixed subject sets.
*RQ1: which x gives the best individual accuracy, which the lowest W, and do
the two rankings disagree?*

**E2. Information ceiling without an LLM.** For each condition, a supervised
model (HistGBT / ordinal regression) from the same inputs to the same target,
5-fold over subjects. Reference points: uniform guess, random human draw.
*RQ2: when an LLM condition is bad, is it because the input carries no
information or because the model cannot use it?* This is the control that
makes "demographics are weak" an interpretable result rather than a prompt
artifact. It reproduces the Jackson et al. benchmark on our subjects.

**E3. Compression.** Compare `history` (up to 49 raw values) vs `type_vector`
(3 fitted values) vs `big_five` (5 measured values) at both levels.
*RQ3: how much individual-level information survives compression to a
three-dimensional type vector, and does compression help distributional
alignment?* Prediction from Jackson et al.: types spread the model's outputs
across the human range where the default prompt collapses to one or two
points, so W should improve even if MAE does not.

**E4. Diversity diagnostics.** For every condition, sigma_model / sigma_human
and standardised bias, as in BehaviorBench Table 4, plus W inside demographic
subgroups.
*RQ4: do richer inputs raise accuracy by narrowing diversity (stereotyping)
or by moving each person to the right place?*

**E5. Model type interaction.** Same conditions on the behavior foundation
model.
*RQ5: does fine-tuning on behavior data make a model use x more or less?*

### Hypotheses

- H1. `demographics` ≈ `none` at the individual level on both tracks; its
  supervised ceiling (E2) will also be near chance.
- H2. Behavior-derived inputs (`history`, `type_vector`) dominate at the
  individual level; `history` is the individual-level ceiling among prompts.
- H3. `type_vector` keeps most of `history`'s individual accuracy and beats it
  on W, because it is a smooth low-dimensional prompt.
- H4. `big_five` (measured) beats `demographics` but trails `type_vector`
  (fitted), mirroring the economic-traits-beat-Big-Five result.
- H5. The behavior foundation model gains less from any x than the frontier
  models, consistent with its training improving p(y | c) more than p(y | x, c).

## 6. Type-vector fitting, concretely

For each model: elicit 10 choices for each of the 125 (R, S, T) vectors on
each of the 9 MobLab game roles (11,250 calls; cached). For Track A do the same
over the 50 survey items (62,500 calls; or 3-level Likert, 1,350 calls, as
Jackson et al. did for their trait comparison). Fit each subject by minimum
mean absolute normalised distance between their *history* observations and the
table's medians; ties averaged. The target observation is never used. The
one-dimensional sweep (Figure 2 of the paper) is reproduced first as a sanity
check that the model responds to the traits monotonically.

## 7. Plan

| Phase | Deliverable | When |
| --- | --- | --- |
| 0 | Matched subject tables for both tracks; supervised ceilings (E2); type-vector choice tables for GPT-4.1 and Gemini Flash | week 1 to 2 |
| 1 | Track B full run, 3 models (E1, E3, E4) | week 3 to 4 |
| 2 | Track A full run (E1, E3, E4) | week 5 |
| 3 | Behavior foundation model (E5); write-up; results in BehaviorBench's leaderboard format | week 6 to 7 |

## 8. Open questions for the lab

1. Is (Risk Aversion, Strategic Sophistication, Trust) the type vector you
   want as the "behavior code" condition, or also a learned-prompt condition in
   the style of the KDD E-step assignment per subject?
2. Does the raw MobLab export have country or other demographics for the
   Across-Ctx subjects?
3. Which behavior foundation model should be the fourth model: the fine-tuned
   Qwen3-4B from the BehaviorBench paper, Be.FM-1.5, or Centaur-70B?
4. Budget for GPT-4.1 and Gemini 3.1 Pro calls (roughly 70k calls per model
   across both tracks, plus the type-vector choice tables).

## References (local copies in ../papers_from_jin/)

- Huang, Xie, Song, Zhang, Yang, Yuan, Jackson, Mei. BehaviorBench. arXiv 2606.24162.
- Jackson, Manning, Xie, Yuan, Mei. Modeling Human Behavior with Type Vectors Using AI. arXiv 2608.18265.
- Xie, Gao, Mei. Distributional Alignment for Social Simulation with LLMs: A Mixture Modeling Approach. KDD 2026.
- Xie, Mei, Yuan, Jackson. Using LLMs to Categorize Strategic Situations and Decipher Motivations Behind Human Behaviors. PNAS 2025.
- Ziems, Held, Karaca, Grusky, Hashimoto, Yang. Will Scaling Improve Social Simulation with LLMs? arXiv 2607.02464.
- Zhou et al. OdysSim. arXiv 2606.14199.
