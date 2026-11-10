# What Survives When You Describe a Kind of Person to a Language Model?

Working draft, 2026-11-08. Sections 4 and 5 are placeholders until outputs/roundtrip.json exists. Numbers in sections
1 to 3 come from docs/TYPE_VECTOR_DIAGNOSTICS.md and docs/UPDATE_2026-10-24.md and were checked against output files.

## Abstract

When a language model is asked to stand in for a person, it is first told who the person is: a few demographics, some
trait scores, a written persona, or a list of past answers. We ask how much of a person's behavior survives that step.
Usually nobody can check: a persona stands for one noisy respondent, or for no fixed set of people at all, and
nothing says how well anyone could have predicted the target from the same information. We build personas for groups of
real people whose answers we hold. On eight questionnaires with 1,500 to 2,500 held-out respondents each, we learn 27
groups of people from their answers alone, so we know how each group answers every question and what the data itself
predicts. We describe each group to Gemini 3.5 Flash in four forms, from an 80-word
sketch to a complete item-by-item profile, always withholding the question to be predicted, and score the model's
answers against the group's own held-out members, next to what the data itself predicts at the same capacity. Two
failures appear, and they come apart. Described in prose, the model plays a caricature: its answers sit 1.5 to 2.4 times
as far from the average as the group's own, on every questionnaire, however long the prose. Given the item-level
profile, it stops exaggerating and matches the data on three questionnaires, but stays 2 to 10 points short on five,
because its picture of which answers go together is wrong for those domains, and no form of description changes that.
Three remedies tested under pre-registered rules all fail; asking for the answer distribution is the only one that never
hurts. The round trip gives a way to score any persona against the behavior of the people it summarizes.

## 1. Introduction

Simulating people with language models has one step in common across every method. Silicon samples give the model a
respondent's demographics (Argyle et al. 2023). Digital twins give it an interview transcript or a history of past
answers (Park et al. 2024; Toubia et al. 2025). Type vectors give it three trait levels (Jackson et al. 2026).
Data-driven personas in human-computer interaction give it a written portrait generated from a cluster of users
(Salminen et al.). In each case a description of a person goes in, and behavior comes out. Everything downstream, from
a synthetic survey to an agent-based society, inherits whatever that step gets wrong.

How faithful is the step? Existing evaluations compare the model's answers with human answers and report a gap. They
cannot say where the gap comes from. When a persona built from a respondent's history predicts that respondent poorly
(Jia et al. 2026), three explanations are open, and each calls for a different comparison. The information in play is
what we know about the person from data: here, a group's typical answers to the other questions. First, the target
question may never have been predictable from that information. To rule this out one needs a ceiling: the group's own
most common answer to the target, which is the best any single prediction for the group can do, with no language model
involved. The floor is the most common answer of everyone. If the ceiling is no higher than the floor, knowing the
group tells you nothing about this question, and no description of the group, however perfect, could help. Second,
the description may have dropped or distorted the information. To test this one holds the information fixed and varies
only its form: a prose summary of the group's typical answers, or the complete list of them, item by item. If the list
scores higher than the summary, the loss sits in the prose channel, in how the summary was written or in how the model
read it, and not in the model's ability to use the information once it is stated plainly. Third, the model may be unable to turn the
information into the right answers. To test this one gives the model the complete list and compares with the ceiling;
whatever gap remains is the model's own. The usual designs allow none of these comparisons. Their one baseline, a
model with no context or with demographics, is a floor, not a ceiling. And all three comparisons rest on a stable fact
about what this kind of person typically answers. One respondent's single answer to a question cannot supply it: if the
respondent answered 4 and the model says 5, nothing says whether that is a miss or a correct reading of a kind of
person who typically answers 5. A demographic cell supplies it only weakly, because its members answer very
differently. What is needed is a group of people who answer alike.

We build such groups and run a round trip. On each of eight questionnaires, six from openpsychometrics.org and two
national surveys, we sort respondents into 27 groups by k-means on their answers alone. Each group is now a kind of
person whose behavior we know: its members' answers to every question. We then describe the group to the model, have
the model answer as the described person, and score the answers against the group's own held-out members. Two features
make the test informative. First, the yardstick: the group's own most common answer, which is what the same data
predicts with no language model at all, at the same capacity, since 27 groups match the 27 cells of a three-trait,
three-level type vector. Second, the hidden item: every description leaves out the question being predicted, so the
model can never copy an answer and must infer it from who the group is. That is the use personas are put to, predicting
what has not been asked.

We vary how much the description says, holding the group fixed: an 80-word prose sketch written from the group's twelve
most distinctive other items, a 200-word portrait written from all of them, a profile listing every other item's typical
answer as a scale label, and the same profile in numbers. We measure two things that a single accuracy number hides.
Amplitude: how far the model's typical answer for the group sits from the population average, relative to how far the
group's own typical answer sits. Shape: whether the model's pattern across items correlates with the group's real
pattern. We score at the individual level, as accuracy on held-out members, and at the population level, as the
distance between a synthetic sample built from the described groups and the real distribution of answers. Finally we
test three remedies, damping, a moderation instruction, and asking for the answer distribution, under decision rules
committed before any result was computed.

The two measurements separate two failures. Described in prose, the model plays a caricature. Its answers sit 1.5 to
2.4 times as far from average as the real group's, on all eight questionnaires, and the 200-word portrait is no better
than the 80-word sketch. The direction is right about 80 percent of the time; the model knows which way the group leans
and overshoots. Given the item-level profile, the exaggeration disappears, the ratio sits near 1, and accuracy rises by
4 to 22 points on seven of eight questionnaires. But a complete profile recovers the group only where the model's
picture of the domain is right. On distress, temperament and the General Social Survey it matches the data. On
nerdiness, Machiavellianism, the World Values Survey and two others it stays 2 to 10 points short, and the shortfall
tracks the shape measure, which is the same under all four descriptions. On nerdiness the model's profile is
anti-correlated with the real group's whatever it is told. The form of the description controls amplitude and does not
touch shape. At the population level the two forms fail in opposite directions: prose-described groups produce a
synthetic sample 1.1 to 1.7 times too wide, profiles one 0.5 to 0.9 times too narrow. None of the three remedies passes
the pre-registered bar. Damping and the moderation instruction gain up to 19 points where exaggeration was the whole
problem and lose up to 10 where shape was wrong too. Asking for the distribution never hurts and gives the best
population-level match on the two national surveys. Reasoning changes none of this.

This differs from the closest prior work in what can be seen. Jia et al. (2026) build a persona for each individual
from background variables and past answers on a Dutch panel, score against a no-context model, and find that personas
barely help individuals and compress human variation; with no ground-truth group and no data yardstick, they cannot
tell description loss from model error, and they see only the compression, not the caricature that prose produces. Lee
et al. (2026) have a model write personas from behavioral records and score demographic-group distributions, finding
that personas improve with in-domain history but a demographics-only baseline stays close; their unit is a demographic
cell whose behavior is heterogeneous, not a behavioral type whose behavior is known, and they have no baseline that uses
the same history without a model. Chae et al. (2026) diagnose flattening and caricature between countries; we find both
inside one population, determined only by how the group is described. Cheng et al. (2023) and Wang et al. (2024) measure
caricature in generated text for groups whose true answers are unknown; we measure it in behavior, on the answer scale,
against the group's real members. The one remedy that survives here, asking for a distribution, was proposed by Lee et
al., and we confirm it.

Our contributions are:
1. The round-trip test: a way to score any persona description against the known behavior of the group it summarizes,
   with a same-capacity data yardstick and the predicted item withheld.
2. A decomposition of persona error into amplitude and shape, showing that the form of the description controls the
   first and not the second.
3. A richness curve on eight questionnaires: prose exaggerates regardless of length; item-level profiles are calibrated
   and recover the data on three questionnaires out of eight.
4. A pre-registered comparison of three remedies, showing that fixes for exaggeration are double-edged and that only
   distribution elicitation is safe.
5. Context from type vectors: trait words chosen per questionnaire beat placebo words on all eight, yet type vectors
   beat the most common answer on only two, and an exploratory capacity curve shows why: three trait levels carry about
   as much as one to six data-learned groups.

## 2. Terms used in this paper

The running example is group 14 on the nonverbal-behavior questionnaire: 158 people who gesture a lot, stand close and
speak expressively. The hidden question is "I touch others on the shoulder or arm while talking to them", answered 1
(never) to 5 (very often).

**Training half, test half.** Each questionnaire's respondents are split in two by position in the file. Groups,
typical answers, descriptions and all baselines are built from the training half. Every number reported is scored on
the test half, whose answers are never used to build anything.

**Group.** A set of training-half people who answered alike, found by k-means with 27 groups per questionnaire. Each
person is a point whose coordinates are their answers; k-means finds 27 centers and assigns each person to the nearest.
A group is "a kind of person" whose behavior we know, because we hold its members' answers to every question.

**Centroid.** The mean of a group's scaled answers. Used only to decide which group a test person is nearest to.

**Typical answer.** A group's median answer to one question, rounded to a whole number. Group 14's typical answer to
the hidden question is 3. Typical answers are what the profiles list and what the exaggeration measure compares with.

**Most common answer.** The single answer given by the most people, also called the mode. It is the best one guess for
a set of people, because it is right for the most of them.

**Floor.** The most common answer of everyone in the training half, used as the prediction for every test person. For
the hidden question it is 2, right for 35 percent of people. In the tables this column is "Most common".

**Ceiling.** A group's most common answer to the hidden question, used as the prediction for every test member of that
group. For group 14 it is 3, right for 56 percent of its members. It is a true ceiling for any method that gives all
members of a group the same answer, which every method here does: no description of group 14, however good, can make
the model beat 3 on group 14's members. In the tables this column is "Learned groups".

**Hidden question, hidden item.** The one question whose answer we try to predict for a test person. It is removed from
every description of the group, so the model can never copy it and must infer it from the rest.

**The information.** What we know about a group from data and are allowed to tell the model: its typical answers to all
questions other than the hidden one. The same information is delivered in several forms.

**Form.** How the information is written into the model's system prompt. Four forms are compared; the first two are
prose, the last two are lists.

**Sketch** (prose12 in the tables). An 80-word second-person paragraph, written by the model from the twelve questions
other than the hidden one on which the group differs most from everyone. No numbers, no quoted questions. "You are
someone who communicates with warmth, high energy, and physical closeness..."

**Portrait** (proseall). The same, written from all questions other than the hidden one, in at most 200 words.

**Summary.** Either prose form, sketch or portrait, as opposed to a list.

**Verbal profile** (verbal). Every question other than the hidden one, each with the group's typical answer given as
the scale label: "I gesture when I talk to people. Answer: 'Very often'."

**Numeric profile** (numeric). The same with the number instead of the label: "Answer: [5]". It has the format of the
history condition in the main study, applied to a group's typical answers instead of one person's past answers.

**List.** Either profile, verbal or numeric, as opposed to a summary.

**Round trip.** Real group, then description of the group, then the model's answers as the described person, then
comparison with the real group's members. Whatever is lost on the way shows as a gap.

**Data assignment.** A test person is placed in the group whose centroid is nearest to their answers on the questions
other than the hidden one, and receives the model's answer for that group's description. This is the main scoring; it
is the clean round trip.

**Fitted assignment.** A test person receives the description whose model answers best match the person's own answers
on the other questions, by the rule of Jackson et al. (2026) for type vectors. It needs no data on the target and is
how a type vector is used in practice. Reported as a secondary scoring.

**Type vector.** Jackson et al.'s description of a person by a few trait levels, here three traits at three levels,
giving 27 possible types, the same number as our groups.

**Accuracy.** The share of test people whose hidden answer is predicted exactly.

**Extremity ratio, amplitude.** For each group and question, how far the model's typical answer sits from everyone's
average, in standard deviations, divided by how far the group's own typical answer sits. Averaged over groups and
questions. A ratio of 2 means the model places the group twice as far from average as it really is. Group 14 from the
sketch: 1.93; from the numeric profile: 1.04.

**Direction agreement.** Among questions where a group departs from the average by more than 0.3 standard deviations,
the share where the model's answer departs the same way.

**Pattern correlation, shape.** For one group, the correlation across questions between the model's departures from
average and the group's real departures. Averaged over groups. It asks whether the model moves on the right questions,
regardless of how far.

**Synthetic sample.** For one question, the model's answers for all 27 described groups pooled, each group weighted by
its size. It stands for what a population simulation built from these personas would produce.

**Wasserstein distance.** How far the synthetic sample's distribution of answers is from the real test-half
distribution, as a percentage of the scale. Zero means identical. Reported with the ratio of the synthetic sample's
spread to the real spread, where above 1 is too wide and below 1 too narrow.

**Damping.** A post-hoc fix: shrink the model's answer toward everyone's average by the extremity ratio measured on the
training half, then round.

**Moderation instruction.** A prompt fix: one sentence added after the sketch asking the model to answer as a typical,
not extreme, member.

**Elicited distribution.** A prompt fix: instead of answering as the person, the model is asked what percentage of such
people choose each option. The top option is the prediction, and the percentages form the synthetic sample.

**Learned groups, type vector, placebo traits.** "Learned groups" is the ceiling above. "Type vector" is the chosen
Big Five type vector from the earlier study. "Placebo traits" are meaningless traits such as preference for the color
orange, used in that study to check that choosing real traits matters.

## 3. Related work

Details and the per-paper differences are in docs/RELATED_WORK.md. Beyond the four papers above: Bisbee et al. (2024)
and Dominguez-Olmedo et al. (2024) on the fragility of model survey responses; Hu and Collier (2024) on how little
variance persona variables explain; Peng et al. (2025) on the digital-twin mega-study; Kim and Lee (2023) on fine-tuning
for unasked survey items; Abels et al. (2026) on calibrating under-dispersed value personas, the opposite correction to
the one prose needs here; Salminen and Jansen on data-driven personas, the artifact whose behavioral fidelity the round
trip measures.

## 4. Method

**Data.** Eight questionnaires: six from openpsychometrics.org (nerdiness, vocational interests, Machiavellianism,
depression-anxiety-stress, temperament, nonverbal behavior), the 2022 General Social Survey, and the World Values
Survey wave 7. Item counts 20 to 92. Respondents 1000 onward of each file; half A (even index) is used to learn groups
and write descriptions, half B (1,500 to 2,500 people) is scored. Each person has one held-out target item; all other
observed items are available.

**Groups.** k-means with 27 clusters on half A, features scaled by item range, missing values filled with the half-A
column mean. 27 matches the capacity of a three-trait, three-level type vector. A half-B person is assigned to the
nearest centroid over their non-target items ("data assignment"). The group's prediction is its most common half-A
answer on the target item ("learned groups").

**Descriptions.** For each group and each target item:
- *Sketch (prose12).* Gemini 3.5 Flash writes a second-person description from the 12 non-target items on which the
  group differs most from everyone, in at most 80 words, with no numbers and no quoted items.
- *Portrait (proseall).* The same from all non-target items, in at most 200 words.
- *Verbal profile.* Every non-target item with the group's typical answer given as its scale label.
- *Numeric profile.* Every non-target item with the group's typical answer as a number, in the format of the history
  condition of the main study.

**Answering.** The description is appended to the questionnaire's system prompt. The model answers the target item
three times with thinking off; the median is the prediction. Two scorings: data assignment (the clean round trip) and
fitted assignment (each person gets the description whose answers best match their other answers, the type-vector
rule).

**Mechanism.** For each group and item, the model's typical answer and the group's typical answer are z-scored against
half A. Extremity ratio: mean |z| of the model over mean |z| of the group. Direction agreement: share of items where
both depart from the average in the same direction, among items where the group departs by more than 0.3 sd. Pattern
correlation: mean over groups of the correlation of the two z profiles.

**Remedies.** Damping: shrink the model's answer toward the half-A mean by the condition's extremity ratio, computed on
half A only. Moderation: one sentence asking for a typical, not extreme, member. Elicitation: ask what percentage of
such people choose each option; predict the top option.

**Population level.** For each item, a synthetic sample mixes the 27 groups' draws weighted by group size and is compared
with the real half-B distribution by the Wasserstein-1 distance as a percentage of the scale range, and by the ratio of
synthetic to real standard deviation.

**Pre-registration.** Decision rules, families of tests and Holm correction are in the docstring of
scripts/suite/roundtrip.py, committed before any result was computed (commit b5fe5d3).

## 5. Results

All numbers are from outputs/roundtrip.json (docs/roundtrip_tables.md has every table). Column names follow Section 2: "Most common" is the floor, "Learned groups" the ceiling, sketch and portrait are the prose summaries, verbal and numeric profiles are the lists. Accuracy is on half B under
data assignment unless stated. "Significant" means Holm-adjusted p < 0.05 within the family named in the script.

### 5.1 Richness curve (family F1 and F2)

| Survey | Most common | Type vector | Sketch | Portrait | Verbal profile | Numeric profile | Learned groups |
|---|---|---|---|---|---|---|---|
| Nerdiness | 40.5 | 38.0 | 31.0 | 30.1 | 30.3 | 35.0 | 44.8 |
| Vocational interests | 32.7 | 37.5 | 32.2 | 37.1 | 38.4 | 39.1 | 42.6 |
| Machiavellianism | 35.5 | 37.7 | 38.0 | 37.8 | 33.6 | 35.1 | 42.4 |
| Distress | 34.0 | 51.6 | 44.6 | 45.8 | 53.8 | 54.0 | 53.8 |
| Temperament | 44.8 | 46.8 | 35.2 | 34.6 | 48.0 | 49.9 | 49.6 |
| Nonverbal behavior | 35.9 | 40.8 | 24.6 | 26.8 | 46.0 | 46.6 | 49.0 |
| General Social Survey | 50.8 | 51.2 | 46.2 | 44.6 | 51.0 | 52.3 | 55.0 |
| World Values Survey | 41.6 | 40.1 | 33.6 | 36.9 | 43.0 | 42.0 | 46.4 |

- **An 80-word sketch loses most of the group.** It is below the most common answer on 6 of 8 questionnaires and below
  the learned groups on all 8, by 4 to 24 points.
- **More prose does not help.** The 200-word portrait written from every item differs from the sketch by -1.7 to +4.9
  points; it is significantly better on 3 of 8 and never by more than 5.
- **Item-level profiles help a lot (F1 rule met).** The numeric profile beats the sketch significantly on 7 of 8, by 4 to
  22 points (nonverbal behavior 24.6 to 46.6); the verbal profile on 6 of 8. Labels and numbers do about equally well.
- **A complete profile recovers the group on some questionnaires and not others (F2: neither pre-registered reading
  met).** The numeric profile matches the learned groups on distress (54.0 vs 53.8), temperament (49.9 vs 49.6) and the
  General Social Survey (52.3 vs 55.0, not significant). It stays significantly short on 5 of 8: nerdiness by 9.8,
  Machiavellianism by 7.4, World Values Survey by 4.4, vocational interests by 3.5, nonverbal behavior by 2.4.
- **Fitted assignment** (each person gets the description whose answers best match their own, needing no data on the
  target): the numeric profile scores 35.8 to 54.5 and beats the chosen type vector on 5 of 8, ties on 1 and loses on 2
  (nerdiness, Machiavellianism).

### 5.2 Mechanism

| Survey | Sketch | Portrait | Verbal profile | Numeric profile | Pattern correlation, all six conditions |
|---|---|---|---|---|---|
| Nerdiness | 1.92 | 1.73 | 0.82 | 0.92 | -0.14 to -0.06 |
| Vocational interests | 1.53 | 1.66 | 1.02 | 1.09 | 0.56 to 0.74 |
| Machiavellianism | 1.72 | 1.68 | 1.01 | 1.14 | 0.41 to 0.53 |
| Distress | 1.58 | 1.64 | 1.02 | 1.05 | 0.33 to 0.55 |
| Temperament | 2.09 | 2.19 | 1.39 | 1.12 | 0.51 to 0.63 |
| Nonverbal behavior | 2.36 | 2.26 | 1.10 | 1.08 | 0.68 to 0.81 |
| General Social Survey | 1.69 | 1.72 | 1.05 | 1.07 | 0.40 to 0.48 |
| World Values Survey | 2.10 | 1.93 | 0.99 | 0.98 | 0.36 to 0.66 |

Extremity ratio: how far the model's typical answer for a group sits from the average, relative to how far the group's
own typical answer sits. All prose intervals exclude 1.

- **Prose makes a caricature.** Described in words, short or long, the model answers 1.5 to 2.4 times as far from the
  average as the group really does, on every questionnaire. Given the item-level profile it does not exaggerate at all
  (ratios 0.82 to 1.39, mostly within 0.1 of 1).
- **Direction is mostly right.** Across the sketch, 80 percent of the group's departures of more than 0.3 sd go the
  right way (72 to 92 percent by questionnaire; docs/sketch_audit.md lists the exceptions).
- **The shape is set by the questionnaire, not the description.** The correlation between the model's pattern across
  items and the group's real pattern barely moves across the six conditions: it is negative on nerdiness under every
  condition and above 0.68 on nonverbal behavior under every condition. What the description form changes is amplitude.
  Where the model's picture of which answers go together is right (distress, temperament, nonverbal behavior) a full
  profile recovers the group; where it is wrong (nerdiness, Machiavellianism) no description does.
- **At the population level the two failures have opposite signs.** A synthetic sample built from prose-described
  groups is 1.1 to 1.7 times too spread out; one built from profiles is 0.5 to 0.9 times too narrow, like type vectors
  (0.53 to 0.88) and like Jia et al.'s individual personas. Only elicited distributions sit near 1 (1.0 to 1.4).

### 5.3 Remedies (family F3; a fix "works" if it helps significantly on at least 6 of 8 and never significantly hurts)

| Survey | Sketch | Sketch, damped | Sketch, moderation instruction | Sketch, elicited distribution |
|---|---|---|---|---|
| Nerdiness | 31.0 | 25.2 | 22.1 | 30.1 |
| Vocational interests | 32.2 | 29.5 | 28.4 | 32.4 |
| Machiavellianism | 38.0 | 27.5 | 32.3 | 39.9 |
| Distress | 44.6 | 40.6 | 39.0 | 41.9 |
| Temperament | 35.2 | 44.7 | 41.6 | 41.9 |
| Nonverbal behavior | 24.6 | 43.3 | 35.9 | 28.9 |
| General Social Survey | 46.2 | 44.8 | 49.8 | 50.8 |
| World Values Survey | 33.6 | 32.4 | 36.2 | 37.7 |

- **None passes.** Damping (shrinking answers by the half-A extremity ratio) gains 19 points on nonverbal behavior and 10
  on temperament, and loses 10 on Machiavellianism and 6 on nerdiness. The moderation sentence cuts the exaggeration to
  1.0 to 1.4 and has the same double edge: +11, +6, +4 on three questionnaires, -4 to -9 on four. Both help exactly where
  exaggeration was the whole problem and hurt where the shape was wrong too. Damping does nothing to profiles, which have
  nothing to damp.
- **Asking for the distribution is the safe choice.** It never hurts significantly, helps on 4 of 8 (temperament +6.6,
  General Social Survey +4.5, nonverbal behavior +4.3, World Values Survey +4.1), and at the population level gives the
  best Wasserstein distance of any model condition on 3 of 8, beating even the learned groups' own population
  prediction on the two national surveys (General Social Survey 5.9 vs 10.6; World Values Survey 8.3 vs 9.5).

### 5.4 Reasoning (family F4)

Answering the sketch with thinking on changes accuracy by +1.3 (nerdiness), +0.3 (Machiavellianism), -0.6 (distress)
and -1.0 (nonverbal behavior) points; none is significant after correction, so the pre-registered rule (3 of 4) is not
met. Thinking does not reduce the caricature; the extremity ratio moves from 1.92 to 2.09, 1.72 to 1.82, 1.58 to 1.69
and 2.36 to 2.44 on the four questionnaires, and the pattern correlation is unchanged. The exaggeration is not a
shortcut the model takes when it answers fast.

### 5.5 Context: type vectors and capacity

Trait words chosen per questionnaire beat placebo words on 8 of 8 (significantly on 4), yet the chosen type vector beats
the most common answer on only 2 of 8 (docs/UPDATE_2026-10-24.md). Exploratory capacity curve (scripts/suite/
capacity_curve.py): a type vector with 27 possible labels predicts about as well as sorting people into 1 to 6
data-learned groups, two groups on 5 of 8 questionnaires.

## 6. Discussion

**Two failures, not one.** A description of a kind of person fails in the model's hands in two separable ways. Prose
inflates amplitude: the model plays a caricature, and more words do not fix it. Independently, the model's picture of
which answers go together, the shape, is right on some questionnaires and wrong on others, and no form of description
changes it. The two can be told apart because item-level profiles remove the first without touching the second.

**What to feed a model.** If the aim is one person's answers, give the item-level profile, in numbers or labels, never a
prose summary of it; expect it to match data-learned groups where the questionnaire has one dominant construct the
model understands, and to fall short where the model's folk theory of the domain is off. If the aim is a population
distribution, ask for the distribution rather than sampling answers, as Lee et al. (2026) also found. Do not damp or
moderate blindly: both correct exaggeration and both destroy signal where there was none to correct.

**Relation to prior findings.** Jia et al. (2026) report that individual personas compress human variation; profiles here
do the same (0.5 to 0.9 of the real spread), while prose does the opposite (1.1 to 1.7). Chae et al. (2026) diagnose
flattening and caricature between countries; here both appear within one population depending only on how the group is
described. The failure of type vectors on surveys (2 of 8 above the most common answer) fits the same picture: three
trait levels are a very short prose description.

**Limits.** One model family with thinking off for the main results; three draws; 27 groups; English questionnaires from
self-selected online samples plus two national surveys. The prose descriptions are written by the same model that
answers them, so the design shows that the prose channel loses information but does not separate the writing from the
reading; the right direction on 80 percent of items and the effect of a reader-side moderation sentence point to the
reading, and a test that asks the model to estimate the group's answers from the prose, rather than act them out, would
settle it. Also the
pre-registered F2 rule returned neither reading, so the "complete profile" claim is a per-questionnaire statement, not a
general one.

## References

[From docs/RELATED_WORK.md.]
