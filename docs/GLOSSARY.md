# Glossary

Plain-language definitions of the terms used in this repository. Terms taken from a paper are credited;
everything else is ordinary usage.

## The question and the design

**Input system.** The way a person is described to the model before it is asked to behave like them.
Our five input systems are listed under *conditions* below.

**p(y | x, c).** BehaviorBench's way of writing the problem: the probability of a behavior *y* given the
subject's characteristics *x* and the context *c* (the task). An input system is a choice of *x*.

**Condition.** One experimental setting, named by what the prompt contains about the person:
- `none`: only the task.
- `demographics`: age, gender, country, education, and similar fields.
- `traits` / measured traits: self-reported scores (Big Five scores, political identity, WVS value indices).
- `history`: the person's own answers to the other items, or choices in the other games. BehaviorBench
  calls this partial information about the subject's behavior.
- `type_vector`: the best-fitting type vector placed in the system prompt (see below).
- `type_table`: type-based prediction from the best-fitting type vector, no new model call (see below).
- Combinations such as `demographics+history` include both descriptions.

**Record / subject-item pair.** One unit of evaluation: one person and one target item (or one target
game). All conditions are run on the same records, so differences come only from the description.

**Held-out / leave-one-out.** The target item or game is removed from everything the model is told about
the person. History and type-vector fitting use only the remaining observations.

**Track A / Track B.** Track A is the survey side of BehaviorBench (Big Five items); Track B is the game
side (MobLab economic games). The nine later datasets form the *survey suite*.

**Draw / sample.** One answer from the model for one prompt. The model is stochastic, so repeated
draws differ. Most conditions use one draw per record; the type-vector choice tables use 5 or 10.

## Type vectors (Jackson, Manning, Xie, Yuan and Mei, 2026)

**Type vector.** A vector of trait intensities given to the model as its persona, for example
"Risk Aversion: 2 out of 5, Strategic Sophistication: 4 out of 5, Trust: 3 out of 5". Each trait is on
a short Likert scale (1 to 5 in the games, 1 to 3 in the surveys). With k traits and L levels there are
L^k possible type vectors (125 for the games, 27 for the surveys).

**Type-vector choice table.** For every possible type vector and every game or item, the model's
generated choices (5 or 10 draws). Built once per model; everything else about type vectors is read
from it.

**Best-fitting type vector.** For one person, the type vector whose generated choices are closest to
that person's observed choices in their *other* games or items (mean absolute difference, normalised
by each scale's range). The target is never used. When several types fit equally well they are *ties*.

**Type-based prediction.** Predicting the held-out choice as the median of the best-fitting type's
generated choices in that game or item. No new model call. Ties are averaged.

**Type vector as system prompt.** Putting the best-fitting type vector into the prompt and asking the
model for the held-out choice directly. One new call per record.

## Scores

**Individual level vs distributional level.** BehaviorBench's two views. Individual: is the prediction
right for this person? Distributional: does the spread of predictions across people look like the
spread of real answers? A model can be right about the average and wrong about everyone, so both are
reported.

**Accuracy.** Share of records where the predicted answer equals the person's actual answer.

**MAE / nMAE.** Mean absolute error. In the games, on each game's choice range rescaled to 0 to 100.
In the surveys, "nMAE" is the same rescaling of a Likert answer (so an error of one step on a 1-to-5
scale is 25).

**W, Wasserstein distance.** How far the distribution of predicted answers is from the distribution of
real answers, in the units of the answer scale (0 to 100 after rescaling). Also called earth mover's
distance: the average amount answers would have to be moved to turn one histogram into the other.
Lower is better. Reported per game or per target item, then averaged.

**W floor.** The W you get by comparing the real answers with a bootstrap resample of themselves. It
is sampling noise; nothing can reliably go below it. It depends on how many answers each unit has:
about 1 to 2 in the games (750 answers per game) and 4 to 8 on the surveys (11 to 50 answers per item).

**sd ratio.** Standard deviation of the predictions divided by the standard deviation of the real
answers. 1 means the model spreads its answers as much as people do; 0 means it gives everyone the
same answer.

**Collapse.** An sd ratio near zero: the model gives one answer to everyone, usually when told nothing
about the person.

**Per-item mode.** The most common real answer to each item. Predicting it for everyone is the
simplest baseline and needs no information about the person.

**Supervised ceiling.** How well an ordinary machine-learning model (gradient-boosted trees, HistGBT)
can predict the target from the same input, trained on thousands of other respondents. It estimates how
much information the input *contains*, so an LLM far below it is failing to use information that is
there. Ceilings are reported per input system.

**Tie-breaking.** When several type vectors fit a person equally well (common with one observed
game), which one is used. Picking the first biased the games result; averaging over ties did not.

## Models

**Thinking on / off.** Gemini models can deliberate with hidden reasoning tokens before answering
("thinking on") or answer directly ("thinking off"). Main runs use Gemini 3.5 Flash with thinking off,
matching the non-reasoning models in the lab's papers; the reasoning check uses Gemini 3.8 Flash with
thinking on.

**OpenAI-compatible endpoint / native endpoint.** Two ways of calling the Gemini API. The code uses the
first for non-thinking runs and the second for thinking runs.

## Data

**BehaviorBench** (Huang et al. 2026). The lab's benchmark: 12 behavioral-science tasks built from
MobLab game logs, a Big Five survey, and research literature, scored at both levels.

**MobLab.** An online platform for classroom economics experiments; the source of the game data
(Dictator, Ultimatum, Trust, Public Goods, Bomb Risk, Beauty Contest, Push/Pull).

**Across-Ctx (across-context) task.** BehaviorBench's task of predicting a person's first-round choice in
one game from their choices in other games. Our `history` condition in Track B is this prompt.

**Masked-response task.** BehaviorBench's task of predicting one Big Five answer from the other 49.
Its 997 records are our Track A subjects.

**Big Five / OCEAN.** The five broad personality traits: Openness, Conscientiousness, Extraversion,
Agreeableness, Neuroticism. Measured here by the 50-item IPIP questionnaire (scores 10 to 50 per
trait) or by the 10-item TIPI (scores 1 to 7).

**TIPI.** Ten Item Personality Inventory, a two-item-per-trait Big Five measure included in the
openpsychometrics datasets. Our *measured traits* for those datasets.

**openpsychometrics.** A website that publishes raw responses to personality tests it hosts. Datasets
used: MACH (Machiavellianism), DASS (depression, anxiety, stress), NPAS (nerdy attributes), RIASEC
(vocational interests), FTI (Fisher temperament), NIS (nonverbal immediacy).

**GSS.** The US General Social Survey; we use the 2022 wave.

**SocSci210** (Kolluri et al. 2025). 210 reconstructed social-science experiments with participant
demographic profiles and responses; we use 40 studies from three shards.

**WVS.** World Values Survey, wave 7 (2017 to 2022), 66 countries.

**Value indices (WVS).** Four summary scores that WVS computes for each respondent from blocks of their
answers and ships as columns; our *measured traits* for WVS. Secular values (SACSECVAL, 0 traditional to
1 secular: religiosity, respect for authority, national pride, rule-bending); emancipative values
(RESEMAVAL, 0 to 1: autonomy, gender equality, personal choice, political voice; the target of the KDD
mixture paper); post-materialism (Y001, 0 to 5: Inglehart's priority of self-expression over material
security); autonomy (Y003, -2 to 2: independence and determination versus obedience and faith as
qualities for children). The survey items that feed each index are excluded from the target pool so the
trait cannot contain the answer.

**Likert scale.** A rating scale with a few ordered options, such as 1 = disagree to 5 = agree.

**ISCED.** The international classification of education levels (0 to 8) used by WVS.
