# What should you tell a language model about a person before asking it to behave like them?

Owen Yang, with Jin Huang and Qiaozhu Mei (Foreseer lab, University of Michigan). October 2026.

## The question

Researchers increasingly use large language models as stand-ins for human subjects: predict how a
person will answer a survey item, play an economic game, or respond in an experiment. To do that, the
model has to be told who the person is. Almost everyone tells it the same thing: demographics (age,
gender, country, education). Nobody had checked whether that is the right thing to tell it.

So we asked a simple question. **Holding the model, the task, and the people fixed, how much does the
description of the person change how well the model predicts their behavior?** We compare five ways
of describing the same person:

| Input system | What the model is told | Example |
|---|---|---|
| nothing | only the task | "You are a player in an economics game." |
| demographics | the usual profile | "a 24-year-old female from Canada, graduate degree, Catholic, married..." |
| measured traits | self-reported trait scores | Big Five scores, political identity, value indices |
| behavior history | what the person actually did elsewhere | their answers to other items, choices in other games |
| best-fitting type vector | a type vector (Jackson et al. 2026): three trait intensities on a 1-to-5 scale, fitted to the person's behavior history | "Risk Aversion 2/5, Strategic Sophistication 4/5, Trust 3/5" |

The type vector follows Jackson, Manning, Xie, Yuan and Mei (2026). A type is three traits (Risk
Aversion, Strategic Sophistication, Trust), each at a level from 1 to 5, so there are 5 x 5 x 5 = 125
possible types. Once per model we ask it how each type would play each game (125 types x 9 games x 10
draws). To describe a person, we compare their choices in the games we observed against every type's
choices in those same games and keep the closest type, their best-fitting type vector. The game we
are predicting is never used to fit. For the survey datasets the same is done with three Big Five
trait names at three levels (27 types) over the questionnaire's items.

We score two things, following BehaviorBench (Huang et al. 2026): **individual accuracy** (did the
model get this person's answer right?) and **distributional alignment** (does the spread of the
model's answers across people look like the human spread? measured by Wasserstein distance, W).
These can disagree: a model can be right about the average and wrong about everyone.

## What we did

- **Ten datasets, about 16,000 subject-task pairs, 240,000 model calls.** BehaviorBench's two sources
  (MobLab economic games, 6,262 held-out game choices; a Big Five survey, 997 held-out items), six
  openpsychometrics questionnaires with rich demographics and a measured Big Five (Machiavellianism,
  depression-anxiety-stress, nerdiness, vocational interests, temperament, nonverbal behavior), the
  2022 General Social Survey, SocSci210 (40 real social-science experiments with 16-field profiles),
  and World Values Survey wave 7 (66 countries).
- **One model so far:** Gemini 3.5 Flash with reasoning disabled, one answer per record, the dataset's
  own task prompt. Only the description of the person changes between conditions.
- **Controls.** For every input we also trained an ordinary supervised model (gradient boosting on
  thousands of other respondents) on the same input to predict the same target. That tells us how much
  information each input *contains*, so we can separate "demographics are uninformative" from "the
  model cannot use them". We also report the human bootstrap floor on W and a multi-draw check.

## What we found

**1. Behavior history is the best input, everywhere.** On all ten datasets, the person's own prior
answers or choices beat every other description, by 8 to 27 accuracy points over nothing.

**2. Demographics are usually close to worthless, and sometimes harmful.** Across ten datasets,
demographics changed accuracy by -7 to +7 points. They helped only where they plausibly carry the
answer (country for values on WVS, gender and age for nonverbal behavior). On three datasets they
made the model worse than telling it nothing, and on real social-science experiments a sixteen-field
profile including party and ideology added one point. Added on top of history, demographics never
added more than two points.

| Dataset | nothing | demographics | measured traits | best-fitting type vector | history |
|---|---|---|---|---|---|
| MobLab games (MAE, lower is better) | 30.9 | - | - | 25.4 | 25.0 |
| Big Five items | 29.2% | 30.9% | 40.8% | 37.2% | 48.4% |
| Machiavellianism | 33.2% | 28.5% | 30.9% | 38.0% | 44.2% |
| Depression-anxiety-stress | 25.5% | 30.1% | 40.1% | 48.4% | 52.9% |
| Nerdiness | 34.4% | 27.3% | 33.0% | 28.9% | 37.7% |
| Vocational interests | 22.5% | 27.5% | 26.1% | 30.9% | 49.7% |
| Temperament | 40.7% | 42.2% | 41.6% | 43.5% | 55.7% |
| Nonverbal behavior | 27.0% | 34.3% | 25.3% | 40.9% | 52.2% |
| General Social Survey 2022 | 47.7% | 47.3% | 45.6% | 50.1% | 55.7% |
| SocSci210 experiments | 26.2% | 27.4% | - | - | 42.5% |
| World Values Survey | 34.7% | 41.8% | 39.6% | 38.4% | 53.2% |

**3. The model is worst at using the input it is usually given.** The supervised control shows that
demographics *do* carry 2 to 5 points of information on every dataset. The language model recovers
almost none of it: on six of eight datasets, the model given demographics scores *below* a supervised
model given nothing but each item's most common answer. Given a profile, the model answers as a
stereotype, and the stereotype is wrong more often than the mode. Given behavior history, the model
sits only 3 to 9 points under the supervised ceiling.

**4. Measured traits help only when the trait is the construct being predicted.** Big Five scores add
15 points on distress items (neuroticism) and 12 on Big Five items, and nothing on temperament,
Machiavellianism, or nonverbal behavior. Political identity does not help on the GSS.

**5. A best-fitting type vector beats self-reported trait scores.** A type vector fitted to the
person's other answers beat their measured Big Five scores on six of eight datasets (by 2 to 16
points), and in the economic games it matched the full behavior history on individual accuracy while
cutting distributional error by a third (W 9.7 vs 14.5). A three-dimensional type vector is a lossy summary of a
response record, though: it trailed raw history on every survey dataset, and it fails when the three
fitted traits are the wrong axes for the domain (nerdiness, values).

**6. Without any description, the model collapses.** Told nothing about the person, Gemini reproduces
0 to 50% of the human spread of answers in the games and is below the per-item modal answer on every
survey. Any behavior-derived input restores the spread; demographics restore some of it while lowering
individual accuracy.

## What is new here

- Prior work fixes one description of the person and never compares alternatives: demographics in the
  survey-simulation benchmarks (BehaviorBench, SubPOP, OpinionQA), prose personas in OdysSim, learned
  latent prompts in the KDD mixture paper, behavior history in Centaur. This is the first side-by-side
  comparison on the same subjects, tasks, and model, across ten datasets.
- The supervised control is what makes the demographics result interpretable: the information is
  there, the model does not use it. That points at prompting and training, not at data.
- The best-fitting type vector is tested as a *prediction input* against measured traits and raw history, with a
  leave-one-out protocol and a distributional score, which the type-vector paper did not do.
- The multi-draw check in the games showed that a tie-breaking rule, not sampling noise, explained the
  gap between using the best-fitting type vector as the system prompt and the paper's type-based
  prediction (the median of that type's generated choices); one-game subjects are where
  it matters.

## Caveats

One model, one draw per record, 1,000 subjects per dataset. The type vectors used the same three trait
names (Extraversion, Agreeableness, Neuroticism) on every survey dataset; domain-matched traits would
likely do better. openpsychometrics samples are self-selected; GSS and WVS are probability samples. The
BehaviorBench survey conditions use its first-person framing, so absolute accuracies are not comparable
to its leaderboard.

**Does reasoning change this?** We repeated four datasets with Gemini 3.8 Flash with thinking on
([docs/REASONING_CHECK.md](docs/REASONING_CHECK.md)). Reasoning helps the model read numeric trait scores
(+4 to +5 points) and history (+2 to +4), and does nothing for demographics (-1.6 to +1.1), which stay
4 to 15 points under their information content. The input ordering is unchanged.

## Documents

- [docs/GLOSSARY.md](docs/GLOSSARY.md): definitions of every non-obvious term (type vector, W, sd ratio, ceiling, conditions, datasets).
- [docs/PROPOSAL.md](docs/PROPOSAL.md): the literature and the design.
- [docs/DATA_FEASIBILITY.md](docs/DATA_FEASIBILITY.md): how subjects were matched across sources.
- [docs/RESULTS.md](docs/RESULTS.md): BehaviorBench runs 1 and 2 (games and Big Five), with tables in
  [docs/results_tables.md](docs/results_tables.md).
- [docs/SUITE_RESULTS.md](docs/SUITE_RESULTS.md): the nine additional datasets, with tables in
  [docs/suite_tables.md](docs/suite_tables.md).
- [docs/REASONING_CHECK.md](docs/REASONING_CHECK.md): thinking on vs off on four datasets.

## Reproducing

```bash
uv venv .venv && uv pip install --python .venv/bin/python numpy scipy pandas scikit-learn pyarrow pyreadstat pycountry
echo 'GEMINI_API_KEY=...' > .env
# data: see docs/DATA_FEASIBILITY.md (BehaviorBench + openpsychometrics BIG5) and scripts/suite/build_*.py
python3 scripts/build_type_table.py            # 125 types x 9 games x 10 draws
python3 scripts/run_track_b.py --conditions none history
python3 scripts/fit_type_vectors.py && python3 scripts/type_table_predict.py
python3 scripts/run_track_b.py --conditions type_vector history+type_vector --fits outputs/track_b/gemini-3.5-flash/fits.jsonl
.venv/bin/python scripts/analyze_track_b.py
python3 scripts/suite/build_openpsych.py && python3 scripts/suite/run_suite.py --dataset mach   # etc.
```

Layout: `src/input_systems/` (prompt conditions, provider, subject loaders, games, suite format),
`scripts/` (BehaviorBench tracks), `scripts/suite/` (the nine-dataset suite), `docs/` (write-ups).
`data/` and `outputs/` are not committed; `.env` holds the API key.

## References

- Huang, Xie, Song, Zhang, Yang, Yuan, Jackson, Mei. BehaviorBench: Benchmarking Foundation Models for Behavioral Science Tasks. arXiv 2606.24162.
- Jackson, Manning, Xie, Yuan, Mei. Modeling Human Behavior with Type Vectors Using AI. arXiv 2608.18265.
- Xie, Gao, Mei. Distributional Alignment for Social Simulation with LLMs: A Mixture Modeling Approach. KDD 2026.
- Xie, Mei, Yuan, Jackson. Using LLMs to Categorize Strategic Situations and Decipher Motivations Behind Human Behaviors. PNAS 2025.
- Ziems et al. Will Scaling Improve Social Simulation with LLMs? arXiv 2607.02464. Zhou et al. OdysSim. arXiv 2606.14199.
