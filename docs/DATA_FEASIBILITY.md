# Data feasibility check (2026-10-16)

Question: does the data support the input-system comparison in PROPOSAL.md,
with Gemini 3.5 Flash as the first model? **Yes for both tracks, with the
caveats below.** All numbers measured on the files in `data/` (gitignored).

## Track A: survey behavior (Big Five)

- The BehaviorBench index file does **not** point at raw rows (indices go up to
  9,814 for a 1,000-row task), so subjects were matched by content instead.
- Raw source: the public openpsychometrics BIG5 file (`data/big5_raw/BIG5/data.csv`,
  19,719 rows, 57 columns, 160 countries). It is the same dataset as the Kaggle
  file BehaviorBench cites, and needs no login.
- Matching the Masked-Resp task's 49 known answers against the raw rows by
  item text (codebook mapping) gives an exact, unique row for 997 of 1,000
  records; 3 are ambiguous. The held-out answer in the record equals the raw
  row's value in all 997 cases. These records cover **761 unique subjects**
  (several records share a subject with different target items).
- For every matched subject we therefore have: demographics (age, gender,
  race, handedness, native English, country), all 50 item answers, and the
  five IPIP scores. Every Track A condition (`none`, `demographics`,
  `big_five`, `history`, `type_vector`, combinations) can be built for the
  **same subject and same target item**. Saved as `data/track_a_subjects.jsonl`.
- The Demo-to-Resp and Demo-to-Pers task files cannot be uniquely matched
  (demographics are too coarse: 1,000 records collapse to 619 demographic
  strings; only 28% and 51% match uniquely). We do not need them: the
  `demographics` condition is rebuilt on the 761 matched subjects using
  BehaviorBench's own prompt template.

## Track B: game behavior (MobLab)

- Across-Ctx task: 6,262 records, 3,929 unique users, 9 target games
  (750 each, 262 for Trust Banker). Each record carries `user_id`, the list
  of history games, and the full instruction + choice for every history game,
  so the `history` condition and the game prompts for the type-vector table
  come from the records themselves. Saved as `data/track_b_subjects.jsonl`.
- History size is the main constraint. Records by number of other games
  observed: 1 game 2,523 (40%), 2 games 1,300, 3 games 1,432, 4 or more 1,007.
  Jackson et al. fit types on subjects with at least four other games. Plan:
  run all records, but report results stratified by history size and treat
  3+ (2,439 records) as the primary type-vector analysis.
- Per target game, the 1-history share ranges from 13% (Ultimatum roles) to
  70% (Push/Pull). Push/Pull targets are categorical (Push or Pull), so that
  game uses accuracy instead of MAE.
- The MobLab joint table from the KDD reproduction covers 6,115 of the 6,262
  records but disagrees with the record's own answer 11% of the time
  (different round or session), and lacks Beauty Contest and Push/Pull. Use
  the BehaviorBench records as ground truth; the joint table only as an
  optional supplement.
- No demographics exist in the MobLab release. A `demographics` arm for Track
  B needs the lab's raw export (country at minimum). Ask Jin.

## Gemini 3.5 Flash

- Works through the OpenAI-compatible endpoint with the key in `.env`
  (`gemini-3.5-flash`; `gemini-3.6/3.7/3.8-flash` also listed).
- Default settings make it a **reasoning** model: about 1,450 hidden thinking
  tokens per call, 7.7 s latency, and visibly noisier answers. With thinking
  off (`reasoning_effort: "none"` or `thinking_budget: 0`) latency is 2.5 s,
  about 240 total tokens per call, and the trait sweep is clean and
  monotonic: Risk Aversion 1 to 5 on the Bomb game opens 99 / 52 / 42 / 21 /
  0 boxes (means of 4 samples). This matches Figure 2 of the type-vector paper
  qualitatively. We will run with thinking off, which also matches the
  lab papers' "default, non-reasoning" convention.
- Not deterministic (e.g. Risk Aversion 4 gave 20, 20, 20, 25), so keep 10
  samples per (type, game) as Jackson et al. did.
- Throughput: 40 concurrent calls completed in 3.6 s with no rate-limit
  errors; intermittent HTTP 503 "high demand" responses (about 10% in one
  burst) need a retry wrapper.

## Budget for the first full run (Gemini 3.5 Flash, thinking off)

| Piece | Calls |
| --- | --- |
| Type-vector choices, games: 125 vectors x 8 history roles + 9 targets (17 prompts) x 10 samples | 21,250 |
| Type-vector choices, survey: 125 vectors x 50 items x 10 samples | 62,500 (or 3-level scale: 1,350 x 10) |
| Track B main: 6,262 records x 4 conditions | 25,048 |
| Track A main: 997 records x 6 conditions | 5,982 |

About 115k short calls, roughly 240 tokens each. At 10 calls/s that is
about 3 hours of wall time.

## Still open

1. Country/demographics for MobLab subjects (Jin).
2. Whether to fit survey-side type vectors on the 5-level or 3-level scale.
3. Supervised ceiling models (HistGBT) need no API and can start now.
