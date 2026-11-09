# What Survives When You Describe a Kind of Person to a Language Model?

Working draft, 2026-11-08. Sections 4 and 5 are placeholders until outputs/roundtrip.json exists. Numbers in sections
1 to 3 come from docs/TYPE_VECTOR_DIAGNOSTICS.md and docs/UPDATE_2026-10-24.md and were checked against output files.

## Abstract (draft)

Language models are asked to stand in for people by being told who the person is. We measure how much of a person's
behavior survives that step with a round trip. From eight questionnaires with 2,000 to 5,000 respondents each, we learn
27 groups of people from their answers alone, so we know how each group actually answers. We then describe each group
to Gemini 3.5 Flash in four ways, from an 80-word sketch to a complete item-by-item profile, always leaving out the item
to be predicted, and score the model's answers against the group's own held-out members. Described in prose, the model
plays a caricature: its answers sit 1.5 to 2.4 times as far from the average as the group's own, on every questionnaire,
and a longer portrait does not help. Given the item-level profile it stops exaggerating and recovers the group's
accuracy on three questionnaires, but stays 2 to 10 points short on five, because its picture of which answers go
together is wrong for those domains and no form of description changes it. Of three remedies tested under rules fixed
in advance, none passes; asking for the answer distribution instead of an answer is the only one that never hurts, and
it gives the best population-level match on the two national surveys. The groups themselves beat the most common answer
on all eight questionnaires, so the information is there; the loss is in the description step. We release the test as a
way to score any persona against the behavior of the people it summarizes.

## 1. Introduction

Every method that simulates people with a language model, from silicon samples (Argyle et al. 2023) to digital twins
(Park et al. 2024; Toubia et al. 2025) to synthetic survey respondents (Jia et al. 2026; Lee et al. 2026), has one step
in common: a description of a person goes in, behavior comes out. Descriptions come in many forms, such as demographics,
trait scores, a few trait levels (Jackson et al. 2026), a written persona, or a list of past answers. Whatever the form,
the model has to turn "who this person is" into "what this person does". How faithful is that step?

The question is hard to answer directly because the people a persona stands for are usually not available. We make them
available. From each of eight questionnaires we learn groups of respondents from their answers alone, with k-means, so
that each group is a kind of person whose behavior we know. We then run a round trip: describe the group to the model,
have the model answer as the described person, and compare with the group's own held-out members. Whatever is lost
between the group and its description, or between the description and the answers, appears as a gap. Because the groups
are learned from data, they also give a yardstick that no earlier persona study has used: what the same data predicts
without a language model.

We vary how much the description says, from an 80-word sketch written from the group's twelve most distinctive items to
a complete profile listing every item's typical answer. Every description leaves out the item being predicted, so the
model can never copy; it has to generalize from who the person is to a question the description did not cover. That is
the use case for personas: predicting what has not been asked.

Contributions.
1. A round-trip test that scores a persona description against the known behavior of the group it summarizes, at the
   individual level (accuracy on members' held-out answers) and the population level (distance between a synthetic
   sample built from the described groups and the real answer distribution).
2. A richness curve on eight questionnaires, pre-registered, with a same-capacity data baseline.
3. A mechanism: [exaggeration ratio, direction agreement, pattern correlation], measured against each group's own
   members rather than against countries or text.
4. Three remedies compared under criteria fixed in advance: damping, a moderation instruction, and asking for the
   group's answer distribution (after Lee et al. 2026).
5. Context from type vectors: trait words chosen per questionnaire beat placebo words on 8 of 8 questionnaires, yet type
   vectors beat the most common answer on only 2 of 8.

## 2. Related work

See docs/RELATED_WORK.md for details. In brief: persona studies measure fidelity against no-context or demographic
baselines at the level of demographic groups or countries. Jia et al. (2026) find that individual personas compress
human variation and fail to recover respondent clusters. Lee et al. (2026) find that personas induced from behavioral
data rarely beat demographics, improve with in-domain history, and that asking for a distribution beats single answers.
Chae et al. (2026) diagnose flattening and caricature at the country level. Caricature in persona text is documented by
Cheng et al. (2023) and others. None scores a persona against the known behavior of the group it summarizes, varies
description richness with the predicted item left out, or compares remedies under pre-committed criteria.

## 3. Method

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

## 4. Results

All numbers are from outputs/roundtrip.json (docs/roundtrip_tables.md has every table). Accuracy is on half B under
data assignment unless stated. "Significant" means Holm-adjusted p < 0.05 within the family named in the script.

### 4.1 Richness curve (family F1 and F2)

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

### 4.2 Mechanism

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

### 4.3 Remedies (family F3; a fix "works" if it helps significantly on at least 6 of 8 and never significantly hurts)

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

### 4.4 Reasoning (family F4)

[Pending: sketch answered with thinking on, four questionnaires.]

### 4.5 Context: type vectors and capacity

Trait words chosen per questionnaire beat placebo words on 8 of 8 (significantly on 4), yet the chosen type vector beats
the most common answer on only 2 of 8 (docs/UPDATE_2026-10-24.md). Exploratory capacity curve (scripts/suite/
capacity_curve.py): a type vector with 27 possible labels predicts about as well as sorting people into 1 to 6
data-learned groups, two groups on 5 of 8 questionnaires.

## 5. Discussion

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
self-selected online samples plus two national surveys; descriptions written by the same model that answers them; the
pre-registered F2 rule returned neither reading, so the "complete profile" claim is a per-questionnaire statement, not a
general one.

## References

[From docs/RELATED_WORK.md.]
