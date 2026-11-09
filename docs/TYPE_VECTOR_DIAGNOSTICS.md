# Why type vectors fail on most surveys: diagnostics (2026-11-02)

Context: under a pre-committed rule, chosen Big Five type vectors beat both placebo traits and the most common answer
on 2 of 8 surveys ([update](UPDATE_2026-10-24.md)). This document asks why, using only stored tables and answers, so
no new API calls (`scripts/suite/type_vector_diagnostics.py`). People: half B of records 1000 onward (1,501 to 2,500
per survey); the Big Five set is the one chosen on half A.

## 1. Data-learned types beat trait-word types on every survey

"Learned types" are 27 clusters found by k-means in half A answers: the same number of types as a three-trait,
three-level type vector, but learned from data rather than from trait words. A half B person is assigned to a cluster
by their other answers and predicted with that cluster's most common answer. "Best possible type vector" lets the fit
see the answer being predicted, so it is an upper bound for this trait set.

| Survey | Most common answer | Placebo traits | Chosen type vector | Learned types | Best possible type vector |
|---|---|---|---|---|---|
| Nerdiness | 40.5 | 33.2 | 38.0 | 44.8 | 42.8 |
| Vocational interests | 32.7 | 31.0 | 37.5 | 42.6 | 41.5 |
| Machiavellianism | 35.5 | 33.1 | 37.7 | 42.4 | 45.2 |
| Depression-anxiety-stress | 34.0 | 34.0 | 51.6 | 53.8 | 56.6 |
| Temperament | 44.8 | 44.0 | 46.8 | 49.6 | 50.9 |
| Nonverbal behavior | 35.9 | 39.8 | 40.8 | 49.0 | 45.6 |
| General Social Survey | 50.8 | 48.8 | 51.2 | 55.0 | 58.4 |
| World Values Survey | 41.6 | 38.2 | 40.1 | 46.4 | 43.6 |

Learned types beat the chosen type vector on all eight surveys, by 2.2 to 8.3 points; every paired 95% interval
excludes zero (depression-anxiety-stress narrowly, 0.1 to 4.4). They also beat the most common answer on all eight,
by 4.2 to 19.8 points. So the surveys do have a 27-type structure that predicts individual answers; the type vectors
recover only part of it. On four surveys (nerdiness, vocational interests, nonverbal behavior, World Values Survey)
even the best possible type vector, which sees the answer, scores below learned types out of sample. There the trait
words cannot express the structure, whichever type a person is given.

Caveat: learned types need answers from many people on the same questionnaire; type vectors need none. This is a
test of how expressive the trait-word types are, not a claim that clustering replaces them. Their remaining advantage
would be carrying a person to a new setting, which is untested.

## 2. It is not that the traits fail to move the model

| Survey | Items where no type changes the answer | Spread of type answers vs human spread | Real answers some type gives | Types in use | People on top three types | Model vs human item structure | Variance on first component |
|---|---|---|---|---|---|---|---|
| Nerdiness | 0% | 1.26 | 83% | 9 | 76% | -0.10 | 23% |
| Vocational interests | 0% | 0.92 | 90% | 27 | 39% | +0.54 | 21% |
| Machiavellianism | 0% | 1.13 | 93% | 27 | 29% | +0.96 | 33% |
| Depression-anxiety-stress | 0% | 1.02 | 99% | 24 | 30% | +0.44 | 44% |
| Temperament | 0% | 1.31 | 96% | 21 | 63% | +0.65 | 12% |
| Nonverbal behavior | 0% | 1.38 | 94% | 27 | 61% | +0.95 | 39% |
| General Social Survey | 16% | 0.71 | 90% | 27 | 34% | +0.56 | 14% |
| World Values Survey | 11% | 0.59 | 78% | 27 | 38% | +0.53 | 11% |

- Trait levels move the answers about as much as people differ (spread ratio 0.6 to 1.4), and 78% to 99% of the answers
  people actually gave are produced by some type. Only on the two attitude surveys do some items not respond at all
  (16% and 11%): personality words do not move views on, for example, government spending.
- The model's implied item structure (how answers co-vary across types) matches the human structure closely on
  Machiavellianism (0.96) and nonverbal behavior (0.95) and not on nerdiness (-0.10), where 9 types are used and 76% of
  people fall on three of them.
- Matching structure is not enough: Machiavellianism and nonverbal behavior gain little over the most common answer.

## 3. Where type vectors work (descriptive, 8 surveys)

Across surveys, the type vector's gain over the most common answer rises with the share of answer variance on the first
principal component (Spearman 0.66, p = 0.08) and with reachability (0.71, p = 0.05). Depression-anxiety-stress has
the strongest single factor (44%) and the largest gain (+17.6), and its chosen set includes Neuroticism. With eight
surveys this is a hypothesis: type vectors pay off when a questionnaire is dominated by one factor that a trait word
names.

## 4. Describing the learned types in words does not help (2026-11-02)

Each of the 27 learned groups was described to the model in plain prose (at most 80 words, no numbers, no quoted items,
written by Gemini 3.5 Flash from the group's 12 most distinctive items on half A). Each description then answered every
item three times. "Verbal types" fits each half B person to a description by the type-vector rule; "data assignment"
gives each person the description of the group the data puts them in. Rule committed before results
(`scripts/suite/verbalized_types.py`).

| Survey | Most common answer | Type vector | Verbal types | Verbal types, data assignment | Learned types |
|---|---|---|---|---|---|
| Nerdiness | 40.5 | 38.0 | 35.7 | 33.9 | 44.8 |
| Vocational interests | 32.7 | 37.5 | 36.4 | 32.5 | 42.6 |
| Machiavellianism | 35.5 | 37.7 | 40.0 | 38.4 | 42.4 |
| Depression-anxiety-stress | 34.0 | 51.6 | 46.5 | 44.7 | 53.8 |
| Temperament | 44.8 | 46.8 | 38.5 | 34.7 | 49.6 |
| Nonverbal behavior | 35.9 | 40.8 | 27.3 | 24.4 | 49.0 |
| General Social Survey | 50.8 | 51.2 | 50.0 | 46.4 | 55.0 |
| World Values Survey | 41.6 | 40.1 | 37.8 | 33.6 | 46.4 |

| Survey | Verbal types minus | Gain | 95% CI | Holm p |
|---|---|---|---|---|
| Nerdiness | type vector | -2.2 | -4.6 to +0.1 | 0.1812 |
| Nerdiness | learned types | -9.0 | -11.2 to -6.9 | 0.0000 |
| Vocational interests | type vector | -1.2 | -3.5 to +1.2 | 0.7012 |
| Vocational interests | learned types | -6.3 | -8.6 to -4.0 | 0.0000 |
| Machiavellianism | type vector | +2.3 | +0.2 to +4.4 | 0.1620 |
| Machiavellianism | learned types | -2.4 | -4.4 to -0.5 | 0.0744 |
| Depression-anxiety-stress | type vector | -5.1 | -7.6 to -2.7 | 0.0000 |
| Depression-anxiety-stress | learned types | -7.3 | -9.5 to -5.1 | 0.0000 |
| Temperament | type vector | -8.3 | -11.3 to -5.3 | 0.0000 |
| Temperament | learned types | -11.1 | -14.0 to -8.3 | 0.0000 |
| Nonverbal behavior | type vector | -13.4 | -16.1 to -10.8 | 0.0000 |
| Nonverbal behavior | learned types | -21.7 | -24.3 to -19.1 | 0.0000 |
| General Social Survey | type vector | -1.1 | -4.0 to +1.7 | 0.7012 |
| General Social Survey | learned types | -4.9 | -7.7 to -2.1 | 0.0056 |
| World Values Survey | type vector | -2.3 | -4.4 to -0.1 | 0.1744 |
| World Values Survey | learned types | -8.6 | -10.9 to -6.4 | 0.0000 |

Verbal types beat type vectors on 0 of 8 surveys and are clearly worse on three (depression-anxiety-stress,
temperament, nonverbal behavior) after correction. They fall clearly below learned types on 7 of 8. With data
assignment, where each person gets the description of their own group, accuracy is lower still, often below the most
common answer (nonverbal behavior 24.4% against 49.0% for the group's own most common answer). So a written description
of a real group, given back to the model, does not reproduce that group's answers.

By the rule fixed in advance, this means the limit is not only the choice of trait words: the model does not turn a
description of a kind of person into that person's answers, and plain prose does worse than three numeric trait levels.
Two explanations remain: an 80-word summary of 12 items may drop information, or the model may not render any
description faithfully. The data-assignment result favors the second, because even the right description for each
person loses most of the group's signal; a test with longer, fuller descriptions would separate them.

## 5. Round-trip study (2026-11-09)

The follow-up with richer descriptions, mechanism and remedies is in [docs/PAPER_DRAFT.md](PAPER_DRAFT.md); rules in
`scripts/suite/roundtrip.py`. In short: prose exaggerates, profiles do not, and the shape of the model's picture of a
questionnaire is fixed regardless of description.

## What this adds, positive and negative

Not found in our searches (not exhaustive):
1. **Negative:** on surveys, type vectors built from trait words are beaten on all eight questionnaires by the same
   number of types learned from data, and on four of them even a type chosen with the answer in view falls short. The
   limit is the trait-word basis, not the number of dimensions.
2. **Negative, diagnostic:** the failure is not weak steering or unreachable answers; it is that the model's mapping
   from a description to answers misses which answers go together for real people. Describing data-learned groups in
   prose does not fix it (section 4), and prose does worse than three numeric trait levels.
3. **Positive:** chosen traits beat placebo traits on all eight surveys in point estimate (four after correction), and
   type vectors gain strongly where one dominant factor matches a trait (depression-anxiety-stress).
4. **Hypothesis:** a questionnaire's first-factor share predicts whether type vectors help.

Closest work to read before claiming these: Wang, Wu and Zeevi, "Adaptive Querying with AI Persona Priors" (arXiv
2605.00696, ICML 2026), which treats LLM personas as a latent class model; Jia et al. (arXiv 2605.10659), which reports
that personas fail to recover multivariate respondent structure; Jackson et al. (arXiv 2608.18265), whose
low-dimensional claim this tests on surveys.

## Next experiments that would settle the open questions

1. **Verbalized learned types.** Done (section 4): descriptions do not recover the groups' accuracy. Next is to test
   longer, fuller descriptions to separate lost information from unfaithful rendering.
2. **Factor-matched traits, chosen in advance.** For each survey, name the trait that matches its first factor before
   seeing results and test the first-factor hypothesis on surveys not yet used.
3. **Transfer.** Fit types on one questionnaire and predict another for the same people (Twin-2K-500), the one setting
   where learned clusters cannot be used and type vectors could still earn their place.
