# What Survives When You Describe a Kind of Person to a Language Model?

Working draft, 2026-11-08. Sections 4 and 5 are placeholders until outputs/roundtrip.json exists. Numbers in sections
1 to 3 come from docs/TYPE_VECTOR_DIAGNOSTICS.md and docs/UPDATE_2026-10-24.md and were checked against output files.

## Abstract (draft)

Language models are asked to stand in for people by being told who the person is. We measure how much of a person's
behavior survives that step with a round trip. From eight questionnaires with 2,000 to 5,000 respondents each, we learn
27 groups of people from their answers alone, so we know how each group actually answers. We then describe each group
to Gemini 3.5 Flash in four ways, from an 80-word sketch to a complete item-by-item profile, always leaving out the item
to be predicted, and score the model's answers against the group's own held-out members. [Results: richness curve;
exaggeration ratio; which fixes worked.] The groups themselves predict held-out answers better than the most common
answer on all eight questionnaires; their descriptions [do or do not]. We release the test as a way to score any
persona against the behavior of the people it summarizes.

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

[To be filled from outputs/roundtrip.json: richness table; mechanism table; remedies table; population table; type
vectors as context; reasoning check.]

## 5. Discussion

[What to feed a model; what the failure says about the model's picture of who answers what together; limits: one model
family, three draws, 27 groups, English self-selected online samples plus two national surveys, descriptions written by
the same model that answers them.]

## References

[From docs/RELATED_WORK.md.]
