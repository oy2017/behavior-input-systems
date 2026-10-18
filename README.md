# What should you tell an AI model about a person before asking it to answer like them?

Owen Yang, with Jin Huang and Qiaozhu Mei (Foreseer lab, University of Michigan). October 2026.

## The question

Researchers are starting to use AI language models as stand-ins for real people. The idea is to
ask the model "how would this person answer this survey question?" or "what would this person do
in this game?" instead of recruiting the person. For that to work, the model has to be told who the
person is.

Almost everyone tells it the same thing: the person's age, gender, country, education, and a few
similar facts. We call that a demographic profile. Nobody had checked whether it is the right thing
to tell the model. So we compared five ways of describing the same person:

| Way of describing the person | What the model is told | Example |
|---|---|---|
| nothing | only the question | "You are answering a survey." |
| demographics | the usual profile | "You are a 24-year-old woman from Canada with a graduate degree, Catholic, married." |
| measured traits | scores from a questionnaire the person filled in | "Your Big Five personality scores are: Extraversion 26 out of 50, Neuroticism 42, ..." |
| behavior history | what the person actually said or did elsewhere | their answers to other survey questions, or their choices in other games |
| best-fitting type vector | a short personality summary that we infer from their behavior history | "Risk Aversion 2 out of 5, Strategic Sophistication 4 out of 5, Trust 3 out of 5" |

The last one needs a word of explanation. A *type vector* (from Jackson, Manning, Xie, Yuan and Mei,
2026) is a short list of trait levels, such as the example above. With three traits, each from 1 to 5,
there are 5 x 5 x 5 = 125 possible types. Once per model, we ask it how each of the 125 types would act
in each game. Then, to describe a real person, we look at the games we have seen them play, find the
type whose behavior matches theirs most closely, and use that type as the description. The question we
are trying to predict is never used when choosing the type. For the survey data we do the same with
three Big Five trait names at three levels each (27 types).

We measure two things for every prediction:

- **Individual accuracy**: how often the model's answer for a person matches that person's real answer.
- **Spread** (we call it W in the detailed write-ups): whether the mix of answers the model gives across
  many people looks like the real mix. A model can get the average right while giving everyone the
  same answer, which is useless for studying how people differ. Lower W means the two mixes are closer.

## How we tested it

- **Ten datasets, about 16,000 person-question pairs, 270,000 model calls.** The lab's own benchmark,
  BehaviorBench (economic games played on the MobLab platform, and a Big Five personality survey);
  six online personality questionnaires from openpsychometrics.org that come with rich demographics
  and a short Big Five measure (Machiavellianism, depression-anxiety-stress, nerdiness, vocational
  interests, temperament, nonverbal behavior); the 2022 US General Social Survey; SocSci210, a
  collection of 40 real social-science experiments; and the World Values Survey, covering 66 countries.
- **Fair comparison.** For each dataset we took the same 1,000 people and the same question for each
  person. The only thing that changed between conditions was the description of the person. One AI
  model (Gemini 3.5 Flash) answered everything.
- **A yardstick for "how much could this information predict at best?"** For every way of describing
  a person, we also trained a conventional statistical model on thousands of other real people who gave
  the same facts, and asked it to predict the same answers. This tells us how much predictive
  information each description actually contains. If the AI model does much worse than this yardstick,
  the problem is the AI model, not the information.

## What we found

**1. The person's own past behavior is the best description, on every dataset.** Telling the model
what the person said or did elsewhere beat every other description, on all ten datasets, by 8 to 27
accuracy points over telling it nothing.

**2. The demographic profile is usually close to useless, and sometimes makes things worse.** Across
the ten datasets, adding demographics changed accuracy by anywhere from minus 7 to plus 7 points. It
helped only where the facts plausibly carry the answer: which country someone lives in matters for
their values, and gender and age matter for nonverbal behavior. On three datasets the profile made the
model *less* accurate than no description at all. On the real social-science experiments, a sixteen-item
profile including the person's political party and ideology added one point. And once the model has the
person's history, adding demographics on top never added more than two points.

| Dataset | nothing | demographics | measured traits | best-fitting type vector | history |
|---|---|---|---|---|---|
| MobLab games (average error, lower is better) | 30.9 | - | - | 25.4 | 25.0 |
| Big Five survey items | 29.2% | 30.9% | 40.8% | 37.2% | 48.4% |
| Machiavellianism | 33.2% | 28.5% | 30.9% | 38.0% | 44.2% |
| Depression-anxiety-stress | 25.5% | 30.1% | 40.1% | 48.4% | 52.9% |
| Nerdiness | 34.4% | 27.3% | 33.0% | 28.9% | 37.7% |
| Vocational interests | 22.5% | 27.5% | 26.1% | 30.9% | 49.7% |
| Temperament | 40.7% | 42.2% | 41.6% | 43.5% | 55.7% |
| Nonverbal behavior | 27.0% | 34.3% | 25.3% | 40.9% | 52.2% |
| General Social Survey 2022 | 47.7% | 47.3% | 45.6% | 50.1% | 55.7% |
| SocSci210 experiments | 26.2% | 27.4% | - | - | 42.5% |
| World Values Survey | 34.7% | 41.8% | 39.6% | 38.4% | 53.2% |

Percentages are how often the model's answer exactly matched the person's. The games row is the
average distance between the model's choice and the person's choice on a 0-to-100 scale.

**3. The demographic profile does contain useful information. The model just cannot use it.** This is
the finding we think matters most. Our statistical yardstick, given only the demographic profile, beats
"predict each question's most common answer" by 2 to 5 points on every dataset. So the profile is
worth something. The AI model, given the same profile, usually does *worse* than predicting the most
common answer (on six of eight datasets). In plain terms: when you hand the model a profile, it answers
as a stereotype of that profile, and the stereotype is wrong more often than just guessing the
typical answer. Given behavior history instead, the model comes within 3 to 9 points of the yardstick,
so it uses that information well.

**4. Questionnaire scores help only when the question is about the same thing the scores measure.**
Big Five personality scores add 15 points when predicting depression-and-anxiety answers (which are
closely related to the neuroticism score) and 12 points when predicting other Big Five answers. They
add nothing when predicting temperament, Machiavellianism, or nonverbal behavior, which are different
things. Knowing someone's political identity does not help predict their other social attitudes.

**5. A short personality summary inferred from behavior beats the person's own questionnaire
scores.** On six of eight datasets, the best-fitting type vector, three trait levels we inferred from the
person's other answers, predicted better than the Big Five scores the person reported about themselves,
by 2 to 16 points. In the economic games it matched the full behavior history on individual accuracy
and produced a more realistic spread of answers (W 9.7 versus 14.5). But three numbers cannot hold
everything a full record does: on every survey dataset the full history still won, and the summary
failed on nerdiness and on values, where the three traits we used are simply the wrong ones.

**6. Told nothing, the model gives everyone the same answer.** With no description, Gemini gave
essentially one answer to every "player" in several games (the spread of its answers was 0 to 50% of
the real spread) and was less accurate than the most common answer on every survey. Any description
drawn from behavior restores a realistic spread. Demographics restore part of the spread while
lowering individual accuracy, which is the stereotype effect again.

## Does it help to let the model "think"?

Gemini can deliberate before answering (its "thinking" mode), at several times the cost. We repeated
four datasets with thinking on ([details](docs/REASONING_CHECK.md)). Thinking helped the model use
questionnaire scores (+4 to +5 points) and behavior history (+2 to +4). It did nothing for the
demographic profile (within 2 points of before, still well below the yardstick). The ranking of the
five descriptions did not change.

## What is new here

- Earlier work used one way of describing people and never compared alternatives: demographics in the
  survey benchmarks (BehaviorBench, SubPOP, OpinionQA), written-out personas in OdysSim, behavior
  history in Centaur. Park et al. (2024) showed that agents built from two-hour interviews beat
  demographic agents on the General Social Survey, the Big Five, and games; our finding 1 replicates
  that across ten datasets with a much cheaper form of history.
- The yardstick comparison (finding 3) is new. It separates "the information is not there" from "the
  model cannot use it," and shows the problem is the second one. That points at how models are prompted
  and trained, not at the data.
- Testing the type vector as a *description of a person* against their own questionnaire scores and
  against their full history (finding 5) is new; the paper that introduced type vectors tested them on
  games only and did not compare against measured traits.

## Limits

One AI model, one answer per question, 1,000 people per dataset. The type vectors used the same three
trait names on every survey, which is probably why they failed on nerdiness and values. The
openpsychometrics respondents are self-selected online test takers; the General Social Survey and
World Values Survey are representative samples. The Big Five survey conditions use BehaviorBench's
first-person phrasing, so those accuracies are not comparable with its leaderboard.

## Read more

- [docs/GLOSSARY.md](docs/GLOSSARY.md): every term used here, explained.
- [docs/PROPOSAL.md](docs/PROPOSAL.md): the background literature and the design.
- [docs/DATA_FEASIBILITY.md](docs/DATA_FEASIBILITY.md): how people were matched across data sources.
- [docs/RESULTS.md](docs/RESULTS.md): the BehaviorBench results in full, with
  [tables](docs/results_tables.md).
- [docs/SUITE_RESULTS.md](docs/SUITE_RESULTS.md): the nine other datasets in full, with
  [tables](docs/suite_tables.md).
- [docs/REASONING_CHECK.md](docs/REASONING_CHECK.md): thinking on versus off.

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

Layout: `src/input_systems/` (prompt conditions, API client, subject loaders, games, suite format),
`scripts/` (BehaviorBench), `scripts/suite/` (the other nine datasets), `docs/` (write-ups). `data/` and
`outputs/` are not committed; `.env` holds the API key.

## References

- Huang, Xie, Song, Zhang, Yang, Yuan, Jackson, Mei. BehaviorBench: Benchmarking Foundation Models for Behavioral Science Tasks. arXiv 2606.24162.
- Jackson, Manning, Xie, Yuan, Mei. Modeling Human Behavior with Type Vectors Using AI. arXiv 2608.18265.
- Xie, Gao, Mei. Distributional Alignment for Social Simulation with LLMs: A Mixture Modeling Approach. KDD 2026.
- Xie, Mei, Yuan, Jackson. Using LLMs to Categorize Strategic Situations and Decipher Motivations Behind Human Behaviors. PNAS 2025.
- Park, Zou, Shaw, Hill, Cai, Morris, Willer, Liang, Bernstein. Generative Agent Simulations of 1,000 People. arXiv 2411.10109.
- Ziems et al. Will Scaling Improve Social Simulation with LLMs? arXiv 2607.02464. Zhou et al. OdysSim. arXiv 2606.14199.
