# What Survives When You Describe a Kind of Person to a Language Model?

Working draft, 2026-11-08. Sections 4 and 5 are placeholders until outputs/roundtrip.json exists. Numbers in sections
1 to 3 come from docs/TYPE_VECTOR_DIAGNOSTICS.md and docs/UPDATE_2026-10-24.md and were checked against output files.

## Abstract

When a language model is asked to stand in for a person, it is first told who the person is: a few demographics, some
trait scores, a written persona, or a list of past answers. We ask how much of a person's behavior survives that step.
Usually nobody can check: a persona stands for one noisy respondent, or for no fixed set of people at all, and
nothing says how well anyone could have predicted the target from the same information. We build personas for groups of
real people whose answers we hold. On eight questionnaires with 1,500 to 2,500 held-out respondents each, we learn 27
groups of people from their answers alone, so we know how each group answers every question and what the group's own answers
predict. We describe each group to Gemini 3.5 Flash in four forms, from an 80-word
short paragraph to a complete item-by-item answer list, always withholding the question to be predicted, and score the model's
answers against the group's own held-out members, next to what the group's own answers predict, the group ceiling, at the same capacity. Two
failures appear, and they come apart. Described in a paragraph, the model plays a caricature: its answers sit 1.5 to 2.4 times
as far from the average as the group's own, on every questionnaire, however long the paragraph. Given the item-level
answer list, it stops exaggerating and reaches the group ceiling on three questionnaires, but stays 2 to 10 points short on five,
because its picture of which answers go together is wrong for those domains, and no form of description changes that.
Three remedies tested under rules fixed in advance all fail; asking for percentages is the only one that never
hurts. The group ceiling is itself 4 to 11 points below what a person's own answers predict: reducing a person to a
kind of person has a cost that no persona can avoid. The round trip is a diagnostic that any persona method, model or questionnaire can be put through: it scores a
description against the behavior of the people it summarizes and says where the error comes from.

## 1. Introduction

Simulating people with language models has one step in common across every method. Silicon samples give the model a
respondent's demographics (Argyle et al. 2023). Digital twins give it an interview transcript or a history of past
answers (Park et al. 2024; Toubia et al. 2025). Type vectors give it three trait levels (Jackson et al. 2026).
Data-driven personas in human-computer interaction give it a written long paragraph generated from a cluster of users
(Salminen et al.). In each case a description of a person goes in, and behavior comes out. Everything downstream, from
a simulated survey to an agent-based society, inherits whatever that step gets wrong.

How faithful is the step? Existing evaluations compare the model's answers with human answers and report a gap. They
cannot say where the gap comes from. When a persona built from a respondent's history predicts that respondent poorly
(Jia et al. 2026), three explanations are open, and each calls for a different comparison. The information in play is
what we know about the person from data: here, a group's typical answers to the other questions. First, the target
question may never have been predictable from that information. To rule this out one needs an information ceiling:
what a supervised model predicts for the target from the person's other answers directly, with no language model and
no grouping involved. The floor is the most common answer of everyone. If the information ceiling is no higher than
the floor, the other answers carry nothing about this question, and no description built from them, however perfect,
could help. A second reference, the group ceiling, is the group's most common answer to the target: the best any
method that gives a group one answer can do, and the yardstick for descriptions, which describe a kind of person. The
gap between the two ceilings is the cost of reducing a person to one of 27 kinds, a design choice of the test. Second,
the description may have dropped or distorted the information. To test this one holds the information fixed and varies
only its form: a paragraph of the group's typical answers, or the complete list of them, item by item. If the list
scores higher than the paragraph, the loss sits in the paragraph channel, in how the paragraph was written or in how the model
read it, and not in the model's ability to use the information once it is stated plainly. Third, the model's general knowledge of people may not replace data from this population: the group ceiling is
counted from the group's real answers to the held-out question, and the model, given the group's other answers
stated plainly, must supply that from what it knows about people. Whatever it cannot supply is the model's limit as a
substitute for data, and it has two parts the test does not split: reasoning about which answers go together, and
population-specific facts no general knowledge contains. To test this one gives the model the complete list and compares with the ceiling;
whatever gap remains is the model's own. The usual designs allow none of these comparisons. They compare many inputs,
demographics, trait scores, type vectors, past answers, a model given nothing, which says which input the model uses
better but not how much there was to use: a score of 47 percent could be nearly everything the information held or a
third of it, and only a ceiling built from the same information without a model can tell which. Every baseline in
these designs is a model score, so every one is a floor. And all three comparisons rest on a stable fact
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
three-level type vector. Second, the held-out item: every description leaves out the question being predicted, so the
model can never copy an answer and must infer it from who the group is. That is the use personas are put to, predicting
what has not been asked.

We vary how much the description says, holding the group fixed: the short paragraph, 80 words written from the group's
twelve most distinctive other items; the long paragraph, 200 words written from all of them; the word list, every
other item with the group's typical answer as a scale label; and the number list, the same with numbers. We measure two things that a single accuracy number hides.
Exaggeration: how far the model's typical answer for the group sits from the population average, relative to how far the
group's own typical answer sits. Pattern: whether the model's pattern across items correlates with the group's real
pattern. We score at the individual level, as accuracy on held-out members, and at the population level, as the
distance between a simulated population built from the described groups and the real distribution of answers. Finally we
test three remedies, shrinking, a typical-member sentence, and asking for percentages, under decision rules
committed before any result was computed. Throughout, the model is held fixed and used as the instrument: the study
ranks descriptions and locates the error, it does not rank models. Where it does say something about the model, that
its picture of which answers go together is wrong on some questionnaires, that is a diagnosis of one model on those
domains, and the round trip is built so that any other model can be put through it.

The two measurements separate two failures. Described in a paragraph, the model plays a caricature. Its answers sit 1.5 to
2.4 times as far from average as the real group's, on all eight questionnaires, and the 200-word long paragraph is no better
than the 80-word short paragraph. The direction is right about 80 percent of the time; the model knows which way the group leans
and overshoots. Given the answer list, the exaggeration disappears, the ratio sits near 1, and accuracy rises by
4 to 22 points on seven of eight questionnaires. But a complete answer list recovers the group only where the model's
picture of the domain is right. On distress, temperament and the General Social Survey it reaches the group ceiling. On
nerdiness, Machiavellianism, the World Values Survey and two others it stays 2 to 10 points short, and the shortfall
tracks the pattern correlation, which is the same under all four descriptions. On nerdiness the model's answer list is
anti-correlated with the real group's whatever it is told. The form of the description controls exaggeration and does not
touch pattern. At the population level the two forms fail in opposite directions: paragraph-described groups produce a
simulated population 1.1 to 1.7 times too wide, answer lists one 0.5 to 0.9 times too narrow. None of the three remedies passes
the fixed in advance bar. Shrinking and the typical-member sentence gain up to 19 points where exaggeration was the whole
problem and lose up to 10 where the pattern was wrong too. Asking for percentages never hurts and gives the best
population-level match on the two national surveys. Reasoning changes none of this.

This differs from the closest prior work in what can be seen. Jia et al. (2026) build a persona for each individual
from background variables and past answers on a Dutch panel, score against a no-context model, and find that personas
barely help individuals and compress human variation; with no ground-truth group and no data yardstick, they cannot
tell description loss from model error, and they see only the compression, not the caricature that paragraph produces. Lee
et al. (2026) have a model write personas from behavioral records and score demographic-group distributions, finding
that personas improve with in-domain history but a demographics-only baseline stays close; their unit is a demographic
cell whose behavior is heterogeneous, not a behavioral type whose behavior is known, and they have no baseline that uses
the same history without a model. Chae et al. (2026) diagnose flattening and caricature between countries; we find both
inside one population, determined only by how the group is described. Cheng et al. (2023) and Wang et al. (2024) measure
caricature in generated text for groups whose true answers are unknown; we measure it in behavior, on the answer scale,
against the group's real members. The one remedy that survives here, asking for a distribution, was proposed by Lee et
al., and we confirm it.

The problem is general to every simulation of people from descriptions. We build the diagnostic for one kind of
simulation first, survey respondents, because telling the three causes apart needs ingredients that closed-ended
questionnaires answered by many people provide: a group of known people, a ceiling that can be counted, and a question
that can be held-out. When a model is asked to answer as a
described person, the test measures how much of the real people's behavior comes back and says which of three causes
produced the loss: the data, when the target was never predictable; the description, when it dropped or distorted what
was known; or the model, when its general knowledge could not replace data from this population. The
name follows round-trip translation: data goes to a description and back to behavior, and the test reports what
changed on the way. It applies to any pipeline, a description form read by a model on a kind of people and questions,
whenever real answers from many such people on a shared set of questions exist. Our contributions are:
1. The round trip, a diagnostic for persona descriptions: it scores a description against the known behavior of the
   group it summarizes, with a same-capacity data ceiling and the predicted item withheld, and separates three causes
   of error: nothing to recover, loss in the paragraph channel, and limits of what the model knows.
2. A decomposition of persona error into exaggeration and pattern, showing that the form of the description controls the
   first and not the second.
3. A richness curve on eight questionnaires: paragraph exaggerates regardless of length; answer lists are calibrated
   and reach the group ceiling on three questionnaires out of eight.
4. An intervention test of the split: correcting amplitude alone, by shrinking answers or by a typical-member
   instruction, helps exactly where exaggeration was the whole loss and hurts where the pattern was also wrong.
5. Context from type vectors: trait words chosen per questionnaire beat placebo words on all eight, yet type vectors
   beat the most common answer on only two, and an exploratory capacity curve shows why: three trait levels carry about
   as much as one to six data-ceiling.

## 2. Terms used in this paper

One name per thing. The running example is group 14 on the nonverbal-behavior questionnaire: 158 people who gesture a
lot, stand close and speak expressively. The held-out question is "I touch others on the shoulder or arm while talking to
them", answered 1 (never) to 5 (very often).

**Training half, test half.** Each questionnaire's respondents are split in two. Groups, typical answers, descriptions
and baselines are built from the training half. Every reported number is scored on the test half, whose answers are
never used to build anything.

**Group.** A set of training-half people who answered alike, found by k-means with 27 groups per questionnaire. A group
is a kind of person whose behavior we know, because we hold its members' answers to every question.

**Typical answer.** A group's median answer to one question, rounded to a whole number. Group 14's typical answer to the
held-out question is 3. The answer lists are made of typical answers, and the exaggeration ratio compares with them.

**Most common answer.** The single answer given by the most people. It is the best one guess for a set of people.

**Floor.** Everyone's most common answer, used as the prediction for every test person. For the held-out question it is
2, right for 35 percent of people.

**Information ceiling.** A supervised model's prediction of the held-out answer from the person's other answers
directly, trained on the training half with every observed answer masked in turn, the item id as a feature. It does
not depend on grouping and says whether the held-out answer is predictable from the rest at all. It sits 4 to 11
points above the group ceiling on the eight questionnaires (docs/roundtrip_tables.md).

**Ceiling, group ceiling.** The group's most common answer, used as the prediction for every test member of that group. For group 14
it is 3, right for 88 of its 158 members, 56 percent. It is the highest individual accuracy any method can reach on a
group's members if it gives all of them the same answer, as every method here does: accuracy counts exact matches, and
the most common answer is by definition the one answer that matches the most members. The short paragraph led the model to say
5, right for 15 members; the number list to say 4, right for 47; nothing could have been right for more than 88. The
bound holds for individual accuracy only. It is not a bound on the distribution distance, since one answer per group
makes a simulated population too narrow, and it is computed on the training half, so a method can land a fraction
above it on the test half by chance.

**Held-out question.** The one question we try to predict for a test person. It is removed from every description, so
the model can never copy it.

**Description.** What we tell the model about the group, placed in the system prompt. Four kinds are compared: two
paragraphs and two answer lists. The held-out question is left out of all four.

**Short paragraph.** An 80-word paragraph in the second person, written by the model from the twelve questions, other than the
held-out one, on which the group differs most from everyone. No numbers, no quoted questions. "You are someone who
communicates with warmth, high energy, and physical closeness..." (result files: prose12)

**Long paragraph.** The same kind of paragraph written from all questions other than the held-out one, in at most 200 words.
(result files: proseall)

**Paragraph.** Either the short paragraph or the long paragraph.

**Fact list.** The information written as a bare list, one fact per line, with nothing added or interpreted: for a
group, its typical answer to each question; for demographics, the raw fields. The word list and the number list are
its two spellings here. It is the control every description is compared with: the description that loses no
information, not the one that works best. A description can score above it, which means the writing helped the model
use the facts, and the test reports that gain the same way it reports a loss.

**Word list.** Every question other than the held-out one, each with the group's typical answer given as its scale
label: "I gesture when I talk to people. Answer: 'Very often'." (result files: verbal)

**Number list.** The same with the number instead of the label: "Answer: [5]". (result files: numeric)

**Answer list.** Either the word list or the number list.

**Round trip.** Real group, then description, then the model's answers as the described person, then comparison with
the real group's members. The name follows round-trip translation, where a text is translated out and back to see
what changed; it is not an established term in persona work and is defined here.

**Placed by data.** A test person is put in the group whose members' answers are nearest to their own answers on the
questions other than the held-out one, and receives the model's answer for that group's description. This is the main
scoring.

**Placed by fit.** A test person receives the description whose model answers best match the person's own answers on
the other questions, by the rule Jackson et al. (2026) use for type vectors. Reported as a secondary scoring.

**Type vector.** Jackson et al.'s description of a person by three traits at three levels each, 27 possible types, the
same number as our groups.

**Accuracy.** The share of test people whose held-out answer is predicted exactly.

**Exaggeration ratio.** For each group and question: how far the model's answer sits from everyone's average, in
standard deviations, divided by how far the group's typical answer sits. Averaged over groups and questions. A ratio of
2 means the model places the group twice as far from average as it really is. Group 14 from the short paragraph: 1.93; from the
number list: 1.04.

**Caricature.** The pattern an exaggeration ratio well above 1 describes: the model leans the right way on most questions and leans too far on all of them, like a drawing that keeps every feature and enlarges it. Group 14 is a bit more touchy than average, a 3 where everyone averages 2.1; from the paragraph the model says 5. The word follows Cheng, Durmus and Jurafsky (2023), who used it for persona text; here it is measured in answers, against the real members.

**Direction agreement.** Among questions where a group departs from the average by more than 0.3 standard deviations,
the share where the model's answer departs the same way.

**Pattern correlation.** For one group, the correlation across questions between the model's departures from average
and the group's real departures, averaged over groups. It asks whether the model moves on the right questions,
regardless of how far.

**Simulated population.** For one question, the model's answers for all 27 described groups pooled, each group weighted
by its size. It stands for what a population simulation built from these descriptions would produce.

**Distribution distance.** How far the simulated population's answers are from the real test-half answers, measured by
the Wasserstein distance as a percentage of the scale; zero means identical. Reported with the spread ratio: the
simulated population's standard deviation over the real one, above 1 too wide, below 1 too narrow.

**Shrinking.** A fix applied after the fact: move the model's answer toward everyone's average by the exaggeration ratio
measured on the training half, then round.

**Typical-member sentence.** A fix in the prompt: one sentence after the short paragraph asking the model to answer as a typical,
not extreme, member of the group.

**Percentage question.** A fix in the prompt: instead of answering as the person, the model is asked what percentage of
such people choose each option. The top option is the prediction, and the percentages form the simulated population.

**Placebo traits.** Meaningless traits such as preference for the color orange, used in the earlier type-vector study to
check that choosing real traits matters.

## 3. Related work

Details and the per-paper differences are in docs/RELATED_WORK.md. Beyond the four papers above: Bisbee et al. (2024)
and Dominguez-Olmedo et al. (2024) on the fragility of model survey responses; Hu and Collier (2024) on how little
variance persona variables explain; Peng et al. (2025) on the digital-twin mega-study; Kim and Lee (2023) on fine-tuning
for unasked survey items; Abels et al. (2026) on calibrating under-dispersed value personas, the opposite correction to
the one paragraph needs here; Salminen and Jansen on data-driven personas, the artifact whose behavioral fidelity the round
trip measures.

## 4. Method

**The procedure in general.** Given a respondent-by-question table, a model to use as the simulator, an information
source (what is known about each respondent) and a description method under test (which turns that information into
text), the test has six steps. (1) Split: divide respondents into a training half and a test half, and hold out one
answer from each test respondent. (2) Group: sort respondents into groups of similar people by the information source;
a group can be one person or a segment, and the count is a parameter. (3) Compute the reference scores, three accuracies from the training
half with no model, against which the verdict is read: the floor, the answer most people give; the information ceiling, a supervised predictor of the
held-out answer from the information source; the group ceiling, the most common answer among a group's training
members, which for a group of one does not exist, so the information ceiling serves. (4) Generate the descriptions, two texts per
group from the same information with the held-out question withheld: the fact list, the facts written one per line with nothing added, and the
description produced by the method under test. (5) Simulate and score: run the model twice per group and question, once playing the person the fact list
describes and once playing the person the description under test describes; score every test respondent under each,
and compare each simulated population with the real one. (6) Locate the loss: place the model's scores on the scale the reference scores set and subtract down the ladder, each
gap being one cause:
information ceiling minus floor is cause 1, the data; information ceiling minus group ceiling is the cost of grouping;
description minus fact list is cause 2, the description, with the exaggeration ratio saying how; fact list
minus group ceiling is cause 3, the model: how much of what a statistical learner gets from this population's data
the model's general knowledge fails to replace, given the group's other answers stated plainly. The gap has two parts
the test does not split, the model's reasoning about which answers go together and population-specific facts no general
knowledge contains; the pattern correlation measures the first, and handing the model population base rates (Section
5.6) probes the second. The fact list is the boundary between causes 2 and 3 because it is the one form
that adds nothing and removes nothing; a form that scored above it would move part of cause 3 to the description side,
which is why any such gain is reported. A persona for one real person, as
in digital twins, is the case of groups of size one. The choices below are this study's instance of each step.

**Setting.** The data is a table: one row per respondent, one column per question, each cell a numbered answer with a
word attached by the questionnaire's scale. The method works on that table and nothing else. It holds out one cell per row
and asks how well that cell can be predicted from the rest of the row, by the data alone and by a model given a
description. It therefore applies to closed-ended questionnaires answered by enough people to form groups, here 3,000
to 5,000, and not to open-ended text or to one-off decisions with no shared set of questions.

**Data.** Eight questionnaires: six from openpsychometrics.org (nerdiness, vocational interests, Machiavellianism,
depression-anxiety-stress, temperament, nonverbal behavior), the 2022 General Social Survey, and the World Values
Survey wave 7. Item counts 20 to 92. Respondents 1000 onward of each file; half A (even index) is used to learn groups
and write descriptions, half B (1,500 to 2,500 people) is scored. Each person has one held-out target item; all other
observed items are available.

**Groups.** The recipe under test in the main experiment is a common pipeline in data-driven persona work, segment the
respondents, summarize each segment, simulate (An et al. 2018; Salminen et al. 2021; Jansen et al. 2021; with a
language model as the summarizer, Lee et al. 2026), so a neutral segmentation of our own stands in for any one firm's, and
it is the only way to have a kind of person whose real answers are known. When a recipe brings its own unit, the test
uses the recipe's: its segments, its fitting rule, or no grouping at all for recipes that describe individuals
(Section 5.6). Here: k-means with 27 clusters on half A, features scaled by item range, missing values filled with the half-A
column mean. 27 matches the capacity of a three-trait, three-level type vector. A half-B person is assigned to the
nearest centroid over their non-target items ("placement by data"). The group's prediction is its most common half-A
answer on the target item ("ceiling").

**Descriptions.** For each group and each target item:
- *Short paragraph (paragraph12).* Gemini 3.5 Flash writes a second-person description from the 12 non-target items on which the
  group differs most from everyone, in at most 80 words, with no numbers and no quoted items.
- *Long paragraph (paragraphall).* The same from all non-target items, in at most 200 words.
- *Word list.* Every non-target item with the group's typical answer given as its scale label.
- *Number list.* Every non-target item with the group's typical answer as a number, in the format of the history
  condition of the main study.

**Answering.** The description is appended to the questionnaire's system prompt. The model answers the target item
three times with thinking off; the median is the prediction. Two scorings: placement by data (the clean round trip) and
placement by fit (each person gets the description whose answers best match their other answers, the type-vector
rule).

**Mechanism.** For each group and item, the model's typical answer and the group's typical answer are z-scored against
half A. Exaggeration ratio: mean |z| of the model over mean |z| of the group. Direction agreement: share of items where
both depart from the average in the same direction, among items where the group departs by more than 0.3 sd. Pattern
correlation: mean over groups of the correlation of the two z answer lists.

**Remedies.** Shrinking: shrink the model's answer toward the half-A mean by the condition's exaggeration ratio, computed on
half A only. Typical-member sentence: one sentence asking for a typical, not extreme, member. Percentage question: ask what percentage of
such people choose each option; predict the top option.

**Population level.** For each item, a simulated population mixes the 27 groups' draws weighted by group size and is compared
with the real half-B distribution by the Wasserstein-1 distance as a percentage of the scale range, and by the ratio of
simulated-to-real standard deviation.

**Rules fixed in advance.** Decision rules, families of tests and Holm correction are in the docstring of
scripts/suite/roundtrip.py, committed before any result was computed (commit b5fe5d3).

## 5. Results

All numbers are from outputs/roundtrip.json (docs/roundtrip_tables.md has every table). Column names follow Section 2: "Most common" is the floor, "Ceiling" the ceiling, short paragraph and long paragraph are the paragraphs, verbal and number lists are the lists. Accuracy is on half B under
placement by data unless stated. "Significant" means Holm-adjusted p < 0.05 within the family named in the script.

### 5.0 Reference points (no model involved)

| Questionnaire | Floor | Group ceiling, 27 groups | Information ceiling, supervised from all other answers | Cost of grouping |
|---|---|---|---|---|
| Nerdiness | 40.5 | 44.8 | 51.5 | 6.7 |
| Vocational interests | 32.7 | 42.6 | 53.5 | 10.9 |
| Machiavellianism | 35.5 | 42.4 | 48.4 | 6.0 |
| Distress | 34.0 | 53.8 | 57.9 | 4.1 |
| Temperament | 44.8 | 49.6 | 55.8 | 6.2 |
| Nonverbal behavior | 35.9 | 49.0 | 58.9 | 9.9 |
| General Social Survey | 50.8 | 55.0 | 59.3 | 4.3 |
| World Values Survey | 41.6 | 46.4 | 54.2 | 7.8 |

The held-out answer is predictable from the rest on every questionnaire, by 8 to 23 points over the floor, so cause 1
is ruled out everywhere. Reducing a person to one of 27 groups costs 4 to 11 of those points; that cost is the
test's, since a description must describe a kind of person, and it is not charged to the description or the model.
Causes 2 and 3 are measured against the group ceiling. Pairwise correlations between a held-out item and the others
average only 0.10 to 0.43, so correlation understates what the other answers carry together; the supervised model is
the measure (scripts/suite/information_ceiling.py).

**Reading the verdict as a ladder.** Two questionnaires, scores on half B, each gap labeled by the cause it measures:

| Score | Nonverbal behavior | Gap | Nerdiness | Gap | What the gap is |
|---|---|---|---|---|---|
| Information ceiling | 59 | | 52 | | minus the floor: 23 and 11 points to recover |
| Group ceiling | 49 | 10 | 45 | 7 | cost of 27 kinds |
| Model, number list | 47 | 2 | 35 | 10 | cause 3, the model |
| Model, short paragraph | 25 | 22 | 31 | 4 | cause 2, the description |
| Floor | 36 | | 41 | | |

On nonverbal behavior the description is the culprit; on nerdiness the model's picture of the domain is, and the
paragraph adds a small loss on top.

### 5.1 Richness curve (family F1 and F2)

| Survey | Floor | Type vector | Short paragraph | Long paragraph | Word list | Number list | Ceiling |
|---|---|---|---|---|---|---|---|
| Nerdiness | 40.5 | 38.0 | 31.0 | 30.1 | 30.3 | 35.0 | 44.8 |
| Vocational interests | 32.7 | 37.5 | 32.2 | 37.1 | 38.4 | 39.1 | 42.6 |
| Machiavellianism | 35.5 | 37.7 | 38.0 | 37.8 | 33.6 | 35.1 | 42.4 |
| Distress | 34.0 | 51.6 | 44.6 | 45.8 | 53.8 | 54.0 | 53.8 |
| Temperament | 44.8 | 46.8 | 35.2 | 34.6 | 48.0 | 49.9 | 49.6 |
| Nonverbal behavior | 35.9 | 40.8 | 24.6 | 26.8 | 46.0 | 46.6 | 49.0 |
| General Social Survey | 50.8 | 51.2 | 46.2 | 44.6 | 51.0 | 52.3 | 55.0 |
| World Values Survey | 41.6 | 40.1 | 33.6 | 36.9 | 43.0 | 42.0 | 46.4 |

- **An 80-word short paragraph loses most of the group.** It is below the most common answer on 6 of 8 questionnaires and below
  the ceiling on all 8, by 4 to 24 points.
- **More paragraph does not help.** The 200-word long paragraph written from every item differs from the short paragraph by -1.7 to +4.9
  points; it is significantly better on 3 of 8 and never by more than 5.
- **Item-level answer lists help a lot (F1 rule met).** The number list beats the short paragraph significantly on 7 of 8, by 4 to
  22 points (nonverbal behavior 24.6 to 46.6); the word list on 6 of 8. Labels and numbers do about equally well.
- **A complete answer list recovers the group on some questionnaires and not others (F2: neither fixed in advance reading
  met).** The number list matches the ceiling on distress (54.0 vs 53.8), temperament (49.9 vs 49.6) and the
  General Social Survey (52.3 vs 55.0, not significant). It stays significantly short on 5 of 8: nerdiness by 9.8,
  Machiavellianism by 7.4, World Values Survey by 4.4, vocational interests by 3.5, nonverbal behavior by 2.4.
- **Placement by fit** (each person gets the description whose answers best match their own, needing no data on the
  target): the number list scores 35.8 to 54.5 and beats the chosen type vector on 5 of 8, ties on 1 and loses on 2
  (nerdiness, Machiavellianism).

### 5.2 Mechanism

| Survey | Short paragraph | Long paragraph | Word list | Number list | Pattern correlation, all six conditions |
|---|---|---|---|---|---|
| Nerdiness | 1.92 | 1.73 | 0.82 | 0.92 | -0.14 to -0.06 |
| Vocational interests | 1.53 | 1.66 | 1.02 | 1.09 | 0.56 to 0.74 |
| Machiavellianism | 1.72 | 1.68 | 1.01 | 1.14 | 0.41 to 0.53 |
| Distress | 1.58 | 1.64 | 1.02 | 1.05 | 0.33 to 0.55 |
| Temperament | 2.09 | 2.19 | 1.39 | 1.12 | 0.51 to 0.63 |
| Nonverbal behavior | 2.36 | 2.26 | 1.10 | 1.08 | 0.68 to 0.81 |
| General Social Survey | 1.69 | 1.72 | 1.05 | 1.07 | 0.40 to 0.48 |
| World Values Survey | 2.10 | 1.93 | 0.99 | 0.98 | 0.36 to 0.66 |

Exaggeration ratio: how far the model's typical answer for a group sits from the average, relative to how far the group's
own typical answer sits. All paragraph intervals exclude 1.

- **Paragraphs makes a caricature.** Described in words, short or long, the model answers 1.5 to 2.4 times as far from the
  average as the group really does, on every questionnaire. Given the answer list it does not exaggerate at all
  (ratios 0.82 to 1.39, mostly within 0.1 of 1).
- **Direction is mostly right.** Across the short paragraph, 80 percent of the group's departures of more than 0.3 sd go the
  right way (72 to 92 percent by questionnaire; docs/short paragraph_audit.md lists the exceptions).
- **The pattern is set by the questionnaire, not the description.** The correlation between the model's pattern across
  items and the group's real pattern barely moves across the six conditions: it is negative on nerdiness under every
  condition and above 0.68 on nonverbal behavior under every condition. What the description form changes is exaggeration.
  Where the model's picture of which answers go together is right (distress, temperament, nonverbal behavior) a full
  answer list recovers the group; where it is wrong (nerdiness, Machiavellianism) no description does.
- **What the pattern failure looks like, item by item.** Three cases from the number-list condition, where the model had
  every other typical answer. (1) Machiavellianism, a trusting group whose list said people are not vicious, do work
  without being forced, and can be trusted: on "most people who get ahead in the world lead clean, moral lives" the
  model said 4; 61 of the group's 92 members said 1, as did nearly everyone in the population (mean 1.7). The model
  reasoned from the persona and did not know the item's base rate. (2) Nerdiness, a bookish group whose list said no
  video games and no novel-writing: on "I like to play RPGs (Ex. D&D)" the model said 2; 69 of 91 members said 5. In
  this sample RPG play is near-universal (mean 4.2) and almost unrelated to video games (r = 0.12); the model's folk
  theory links the two. (3) Machiavellianism, a cynical group: on "P.T. Barnum was wrong when he said there's a sucker
  born every minute" the model said 1, as a literal reading of a cynic implies; 70 of 114 members said 5. The item is a
  double negative that respondents parse inconsistently, and no reader of the text could predict this group's answer.
  So the pattern gap mixes two things: population facts about items that the model does not know and the data does,
  and respondent or dataset quirks that only the data can carry.
- **At the population level the two failures have opposite signs.** A simulated population built from paragraph-described
  groups is 1.1 to 1.7 times too spread out; one built from answer lists is 0.5 to 0.9 times too narrow, like type vectors
  (0.53 to 0.88) and like Jia et al.'s individual personas. Only percentage questions sit near 1 (1.0 to 1.4).

### 5.3 Intervening on amplitude alone: a test of the two-part split (family F3)

| Survey | Short paragraph | Short paragraph, shrunk | Short paragraph, typical-member sentence | Short paragraph, percentage question |
|---|---|---|---|---|
| Nerdiness | 31.0 | 25.2 | 22.1 | 30.1 |
| Vocational interests | 32.2 | 29.5 | 28.4 | 32.4 |
| Machiavellianism | 38.0 | 27.5 | 32.3 | 39.9 |
| Distress | 44.6 | 40.6 | 39.0 | 41.9 |
| Temperament | 35.2 | 44.7 | 41.6 | 41.9 |
| Nonverbal behavior | 24.6 | 43.3 | 35.9 | 28.9 |
| General Social Survey | 46.2 | 44.8 | 49.8 | 50.8 |
| World Values Survey | 33.6 | 32.4 | 36.2 | 37.7 |

- **The prediction of the two-part split holds.** If the loss under a paragraph has an amplitude part and a pattern part, an
  intervention on amplitude alone should help where amplitude was the whole loss and hurt where the pattern was also
  wrong. Shrinking (shrinking answers by the half-A exaggeration ratio) gains 19 points on nonverbal behavior and 10
  on temperament, and loses 10 on Machiavellianism and 6 on nerdiness. The typical-member sentence cuts the exaggeration to
  1.0 to 1.4 and has the same double edge: +11, +6, +4 on three questionnaires, -4 to -9 on four. Both help exactly where
  exaggeration was the whole problem and hurt where the pattern was wrong too. Shrinking does nothing to answer lists, which have
  nothing to shrink.
- **Asking for percentages is the safe choice.** It never hurts significantly, helps on 4 of 8 (temperament +6.6,
  General Social Survey +4.5, nonverbal behavior +4.3, World Values Survey +4.1), and at the population level gives the
  best distribution distance of any model condition on 3 of 8, beating even the ceiling' own population
  prediction on the two national surveys (General Social Survey 5.9 vs 10.6; World Values Survey 8.3 vs 9.5).

### 5.4 Reasoning (family F4)

Answering the short paragraph with thinking on changes accuracy by +1.3 (nerdiness), +0.3 (Machiavellianism), -0.6 (distress)
and -1.0 (nonverbal behavior) points; none is significant after correction, so the fixed in advance rule (3 of 4) is not
met. Thinking does not reduce the caricature; the exaggeration ratio moves from 1.92 to 2.09, 1.72 to 1.82, 1.58 to 1.69
and 2.36 to 2.44 on the four questionnaires, and the pattern correlation is unchanged. The exaggeration is not a
shortcut the model takes when it answers fast.

### 5.5 The round trip with outside information: personas from demographics and trait scores

The same test on descriptions built from outside the survey, run on the main study's 1,000 records per questionnaire
with the unit being the individual (so the group ceiling is the information ceiling, the supervised model trained on the
same fields, and there is no cost of grouping). The fact list is the raw fields, already run in the main study; the
description under test is an 80-word second-person persona the model writes from the fields. Rules in
scripts/suite/persona_fields.py; full tables in docs/roundtrip_tables.md.

| Information | Ceiling − floor | Raw fields − ceiling | Persona − raw fields | Rule verdict |
|---|---|---|---|---|
| Demographics, 8 questionnaires | +0.8 to +5.4 | −2.2 to −14.0; below the floor on 8 of 8 | −1.9 to −5.3; significant on 2 of 8 | form does not matter |
| Demographics + trait scores, 8 | +3.1 to +10.6 | −3.2 to −16.1 | −7.7 (distress, significant) to +3.6; significant on 1 of 8 | form does not matter |

Two ladders: nerdiness with demographics, floor 40.1, ceiling 41.3, raw fields 27.3, persona 24.9; distress with
demographics and trait scores, floor 33.8, ceiling 44.4, raw fields 41.2, persona 33.5.

- **With outside information the dominant loss is the model's.** Given the plain demographics it scores below the
  floor on every questionnaire: knowing a person's age and gender makes it worse than knowing nothing. This is the main
  study's demographics result placed on the ladder.
- **Writing the fields into a persona adds a small loss on top,** 2 to 5 points with demographics, in the same direction
  on all eight but significant on two, so the pre-committed rule returns "the form does not matter". With trait scores
  the persona's loss concentrates where the fields carried the most, distress, where Neuroticism predicts the answers.
- **Mirror image of the main round trip.** There the model used the fact list well and the paragraph destroyed it; here
  the paragraph matters little because the model has already lost nearly everything by the time it reads the plain
  fields. The same diagnostic gives opposite verdicts, and both match what the main study found by other means.
- Deviation from the rule as written: the trait condition was fixed in advance for six questionnaires; the two national
  surveys also carry trait-like scores (political identity; value indices), so eight were run and the same six-of-eight
  threshold was applied.

### 5.6 Three published recipes on the ladder

The diagnostic is only useful if it can be pointed at real methods. Three recipes from the literature are re-run with
our model and prompts on our questionnaires (the published numbers cannot be placed without the authors' prompts and
personas).

**Type vectors (Jackson et al. 2026).** Three trait levels as the description, placed by fit; the fact list placed by the
same rule is the control; the group ceiling is the yardstick.

| Questionnaire | Type vector | Fact list, placed by fit | Group ceiling | What 3 levels lose | What the model cannot replace |
|---|---|---|---|---|---|
| Nonverbal behavior | 40.8 | 47.1 | 49.0 | 6.4 | 1.9 |
| Vocational interests | 37.5 | 42.2 | 42.6 | 4.7 | 0.4 |
| Temperament | 46.8 | 50.7 | 49.6 | 3.9 | 0 |
| Distress | 51.6 | 54.5 | 53.8 | 2.9 | 0 |
| World Values Survey | 40.1 | 42.9 | 46.4 | 2.8 | 3.6 |
| General Social Survey | 51.2 | 51.2 | 55.0 | 0.1 | 3.7 |
| Nerdiness | 38.0 | 36.6 | 44.8 | 0 | 8.2 |
| Machiavellianism | 37.7 | 35.8 | 42.4 | 0 | 6.6 |

On four questionnaires the short description is the loss, 3 to 6 points, and the model with the full facts is at the
ceiling. On nerdiness and Machiavellianism the type vector loses nothing beyond what the full facts lose: the limit is
the model's picture of the domain, and no richer description would help. The type-vector paper's own setting is
economic games, where the main study found type vectors competitive with history; the diagnosis here is for surveys.

**Silicon samples (Argyle et al. 2023).** A backstory written from demographics: Section 5.5, demographics rows. Little
to recover; the model given the raw fields is below the floor on 8 of 8; the backstory costs 2 to 5 more.

**Profiles from a person's own history (Jia et al. 2026; Lee et al. 2026).** A profile the model writes from the
person's answers to the other questions, against those answers as a list (the main study's history condition) and the
supervised model on them. [Run in progress; rule in scripts/suite/persona_fields.py.]

### 5.7 Context: type vectors and capacity

Trait words chosen per questionnaire beat placebo words on 8 of 8 (significantly on 4), yet the chosen type vector beats
the most common answer on only 2 of 8 (docs/UPDATE_2026-10-24.md). Exploratory capacity curve (scripts/suite/
capacity_curve.py): a type vector with 27 possible labels predicts about as well as sorting people into 1 to 6
data-ceiling, two groups on 5 of 8 questionnaires.

## 6. Discussion

**Two failures, not one.** A description of a kind of person fails in the model's hands in two separable ways. Paragraphs
inflates exaggeration: the model plays a caricature, and more words do not fix it. Independently, the model's picture of
which answers go together, the pattern, is right on some questionnaires and wrong on others, and no form of description
changes it. The two can be told apart because answer lists remove the first without touching the second.

**When to use the diagnostic.** Before trusting a persona pipeline, run the round trip on questions that have already
been asked. A market researcher who builds personas from customer segments learns which form to write them in and how
far to trust their answers to new questions. A social scientist building silicon samples or digital twins learns
whether a gap comes from the description or from the model's picture of the domain before interpreting the twins. A
model developer gets an audit of the model's folk psychology: the pattern correlation by questionnaire, and the item
audit behind it, show which domains the model misreads. The test needs respondents on a shared item set, a split, and
the model; it returns a floor, a ceiling, accuracy per form, the exaggeration ratio, the pattern correlation and the
distribution distance, and the verdict is read from where a form falls between floor and ceiling and from which measure
explains the gap.

**The roles of the four forms.** The two lists are the reference: the information in its fact list, which every
comparison needs. The two paragraphs are the forms under test, and they are the method most persona pipelines use, a
model summarizing a segment into prose. Another generator is added beside the paragraphs and compared with the same
list; the list stays. The list is not assumed to be the best description: the group ceiling sits above it on five of
eight questionnaires, so a better description can exist, and the percentage question already beats it at the
population level on three.

**Testing someone else's description method.** Any generator slots into the test as one more form, provided two
reference points can be built from the same information the generator uses: a data-only ceiling, what a statistical
predictor gets from that information with no model, and the fact list of that information, the facts with no
writing. For descriptions built from survey answers, as here, the ceiling is the group's most common answer and the
fact list is the list. For descriptions built from demographics, the ceiling is the most common answer within each
demographic cell and the fact list is the demographic fields themselves; the main study's supervised yardstick on
demographics is this comparison. The generator's description against the fact list then measures what the writing
lost, and the fact list against the ceiling measures what the model cannot use. The one condition is that the
information the descriptions come from must be available for the respondents being scored; a persona built from an
interview can be tested only on respondents who were interviewed. For information that is continuous and per person,
such as trait scores, the ceiling is a supervised predictor rather than a cell's most common answer, a strong yardstick
rather than a strict bound. Two of the three legs already exist for demographics and trait scores from the main study:
the fields themselves were the demographics and traits conditions, and the supervised yardstick was the ceiling, which
sat 1 to 5 points above the floor while the model given demographics sat below it. The third leg, a persona written from those
fields compared with the raw fields, is run in Section 5.5: the writing adds a small loss on top of the model's large
one.

**What to feed a model.** If the aim is one person's answers, give the answer list, in numbers or labels, never a
paragraph of it; expect it to match data-ceiling where the questionnaire has one dominant construct the
model understands, and to fall short where the model's folk theory of the domain is off. If the aim is a population
distribution, ask for percentages rather than sampling answers, as Lee et al. (2026) also found. Do not shrink or
moderate blindly: both correct exaggeration and both destroy signal where there was none to correct.

**Relation to prior findings.** Jia et al. (2026) report that individual personas compress human variation; answer lists here
do the same (0.5 to 0.9 of the real spread), while paragraph does the opposite (1.1 to 1.7). Chae et al. (2026) diagnose
flattening and caricature between countries; here both appear within one population depending only on how the group is
described. The failure of type vectors on surveys (2 of 8 above the most common answer) fits the same picture: three
trait levels are a very short paragraph description.

**Limits.** Surveys only: six questionnaires from openpsychometrics.org and two national surveys, no economic games.
Type vectors were built for games and matched past history there in the main study, so the two failures found here may
not appear in games; the round trip applies there unchanged, grouping players by their choices, and is the natural next
test. One model family with thinking off for the main results; three draws; 27 groups; English questionnaires from
self-selected online samples plus two national surveys. The paragraph descriptions are written by the same model that
answers them, so the design shows that the paragraph channel loses information but does not separate the writing from the
reading; the right direction on 80 percent of items and the effect of a reader-side typical-member sentence point to the
reading, and a test that asks the model to estimate the group's answers from the paragraph, rather than act them out, would
settle it. Part of the pattern gap is item base rates and
respondent quirks that no reader of a description can know, so the ceiling is a ceiling on information, not only on
reasoning; giving the model each item's population distribution alongside the list is the natural next test, and the
main study found such base rates help. The population comparison is made on the whole test half per question, not group by group: a group's
three draws are nearly always identical, so the model offers no within-group distribution to compare with its members'
spread; only the percentage question produces one, and it is pooled rather than scored per group. Also the
fixed in advance F2 rule returned neither reading, so the "complete answer list" claim is a per-questionnaire statement, not a
general one.

## References

[From docs/RELATED_WORK.md.]
