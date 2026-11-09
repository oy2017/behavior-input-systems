# Round-trip study: all tables

Generated 2026-11-09 by `scripts/suite/roundtrip.py --analyze` from outputs/roundtrip.json. Decision rules are in the script docstring; the write-up is docs/PAPER_DRAFT.md. Conditions: prose12 = 80-word sketch, proseall = 200-word portrait, verbal = item-level profile with scale labels, numeric = item-level profile with numbers, moderate = sketch plus a moderation sentence, elicit = sketch with the answer distribution asked for, think = sketch with thinking on (four questionnaires).

Accuracy on half B, data assignment (%)
| Survey | Most common | Type vector | prose12 | proseall | verbal | numeric | moderate | elicit | think | Learned groups |
|---|---|---|---|---|---|---|---|---|---|---|
| Nerdiness | 40.5 | 38.0 | 31.0 | 30.1 | 30.3 | 35.0 | 22.1 | 30.1 | 32.3 | 44.8 |
| Vocational interests | 32.7 | 37.5 | 32.2 | 37.1 | 38.4 | 39.1 | 28.4 | 32.4 |  | 42.6 |
| Machiavellianism | 35.5 | 37.7 | 38.0 | 37.8 | 33.6 | 35.1 | 32.3 | 39.9 | 38.2 | 42.4 |
| Distress | 34.0 | 51.6 | 44.6 | 45.8 | 53.8 | 54.0 | 39.0 | 41.9 | 44.0 | 53.8 |
| Temperament | 44.8 | 46.8 | 35.2 | 34.6 | 48.0 | 49.9 | 41.6 | 41.9 |  | 49.6 |
| Nonverbal behavior | 35.9 | 40.8 | 24.6 | 26.8 | 46.0 | 46.6 | 35.9 | 28.9 | 23.6 | 49.0 |
| General Social Survey | 50.8 | 51.2 | 46.2 | 44.6 | 51.0 | 52.3 | 49.8 | 50.8 |  | 55.0 |
| World Values Survey | 41.6 | 40.1 | 33.6 | 36.9 | 43.0 | 42.0 | 36.2 | 37.7 |  | 46.4 |

Damped accuracy (factor from half A)
| Survey | prose12 | proseall | verbal | numeric | moderate | elicit | think |
|---|---|---|---|---|---|---|---|
| Nerdiness | 25.2 | 26.8 | 30.3 | 35.0 | 21.6 |  | 24.6 |
| Vocational interests | 29.5 | 31.3 | 38.4 | 39.1 | 28.4 |  |  |
| Machiavellianism | 27.5 | 28.6 | 33.6 | 35.1 | 30.8 |  | 27.0 |
| Distress | 40.6 | 39.4 | 53.8 | 54.0 | 39.0 |  | 37.5 |
| Temperament | 44.7 | 46.1 | 48.1 | 49.9 | 41.9 |  |  |
| Nonverbal behavior | 43.3 | 43.9 | 46.0 | 46.6 | 41.0 |  | 44.6 |
| General Social Survey | 44.8 | 44.3 | 51.0 | 52.3 | 49.2 |  |  |
| World Values Survey | 32.4 | 36.0 | 43.0 | 42.0 | 35.9 |  |  |

Extremity ratio, model over group [95% CI over groups]; direction agreement; pattern correlation
| Survey | prose12 | proseall | verbal | numeric | moderate | elicit | think |
|---|---|---|---|---|---|---|---|
| Nerdiness | 1.92 [1.63, 2.25]; 72%; -0.08 | 1.73 [1.52, 1.97]; 67%; -0.10 | 0.82 [0.75, 0.88]; 66%; -0.10 | 0.92 [0.84, 0.99]; 62%; -0.14 | 1.26 [1.00, 1.55]; 66%; -0.09 | 2.01 [1.68, 2.38]; 70%; -0.06 | 2.09 [1.78, 2.45]; 73%; -0.09 |
| Vocational interests | 1.53 [1.37, 1.71]; 77%; 0.65 | 1.66 [1.49, 1.85]; 93%; 0.74 | 1.02 [0.98, 1.06]; 93%; 0.72 | 1.09 [1.05, 1.13]; 92%; 0.72 | 1.00 [0.91, 1.11]; 76%; 0.63 | 1.45 [1.29, 1.65]; 74%; 0.56 |  |
| Machiavellianism | 1.72 [1.55, 1.92]; 81%; 0.53 | 1.68 [1.52, 1.85]; 81%; 0.53 | 1.01 [0.96, 1.05]; 78%; 0.43 | 1.14 [1.10, 1.19]; 79%; 0.41 | 1.36 [1.18, 1.56]; 78%; 0.49 | 1.58 [1.43, 1.75]; 82%; 0.51 | 1.82 [1.63, 2.04]; 82%; 0.51 |
| Distress | 1.58 [1.39, 1.82]; 88%; 0.33 | 1.64 [1.46, 1.85]; 91%; 0.46 | 1.02 [0.99, 1.05]; 90%; 0.55 | 1.05 [1.03, 1.08]; 90%; 0.54 | 1.00 [0.78, 1.27]; 87%; 0.34 | 1.29 [1.08, 1.53]; 87%; 0.35 | 1.69 [1.50, 1.95]; 87%; 0.28 |
| Temperament | 2.09 [1.89, 2.32]; 81%; 0.58 | 2.19 [2.00, 2.40]; 85%; 0.63 | 1.39 [1.33, 1.45]; 83%; 0.56 | 1.12 [1.07, 1.18]; 82%; 0.54 | 1.33 [1.18, 1.51]; 77%; 0.51 | 1.52 [1.36, 1.69]; 79%; 0.55 |  |
| Nonverbal behavior | 2.36 [2.08, 2.69]; 92%; 0.74 | 2.26 [2.01, 2.54]; 95%; 0.80 | 1.10 [1.06, 1.15]; 92%; 0.76 | 1.08 [1.04, 1.13]; 93%; 0.81 | 1.42 [1.24, 1.63]; 90%; 0.68 | 2.00 [1.76, 2.30]; 91%; 0.73 | 2.44 [2.15, 2.77]; 92%; 0.73 |
| General Social Survey | 1.69 [1.57, 1.81]; 78%; 0.40 | 1.72 [1.60, 1.86]; 79%; 0.42 | 1.05 [1.02, 1.08]; 79%; 0.48 | 1.07 [1.04, 1.10]; 79%; 0.47 | 1.33 [1.26, 1.41]; 78%; 0.43 | 1.41 [1.33, 1.49]; 77%; 0.42 |  |
| World Values Survey | 2.10 [1.92, 2.33]; 75%; 0.36 | 1.93 [1.75, 2.14]; 83%; 0.47 | 0.99 [0.95, 1.02]; 83%; 0.59 | 0.98 [0.96, 1.00]; 86%; 0.66 | 1.24 [1.12, 1.37]; 75%; 0.37 | 1.59 [1.44, 1.76]; 77%; 0.38 |  |

Fitted assignment accuracy (type-vector rule)
| Survey | prose12 | proseall | verbal | numeric | moderate | elicit | think |
|---|---|---|---|---|---|---|---|
| Nerdiness | 35.0 | 34.9 | 34.9 | 36.6 | 24.6 |  | 36.2 |
| Vocational interests | 36.0 | 37.6 | 40.4 | 42.2 | 29.8 |  |  |
| Machiavellianism | 38.4 | 37.0 | 35.0 | 35.8 | 31.9 |  | 39.8 |
| Distress | 47.2 | 47.1 | 54.2 | 54.5 | 42.1 |  | 46.1 |
| Temperament | 36.7 | 36.4 | 49.0 | 50.7 | 43.8 |  |  |
| Nonverbal behavior | 27.4 | 30.4 | 45.6 | 47.1 | 39.2 |  | 28.0 |
| General Social Survey | 49.6 | 48.8 | 51.2 | 51.2 | 51.1 |  |  |
| World Values Survey | 38.4 | 37.9 | 43.8 | 42.9 | 39.6 |  |  |

Population level: Wasserstein distance of the synthetic sample to the real answers (% of scale; lower is better) / synthetic-to-real sd ratio
| Survey | mode | type_vector | prose12 | proseall | verbal | numeric | moderate | elicit | think | learned |
|---|---|---|---|---|---|---|---|---|---|---|
| Nerdiness | 30.3 / 0.00 | 15.2 / 0.73 | 16.4 / 1.34 | 15.1 / 1.21 | 15.8 / 0.61 | 15.3 / 0.63 | 19.0 / 0.84 | 18.4 / 1.16 | 18.4 / 1.45 | 8.1 / 0.94 |
| Vocational interests | 33.9 / 0.00 | 11.2 / 0.82 | 12.3 / 1.18 | 13.1 / 1.28 | 8.6 / 0.81 | 8.2 / 0.86 | 12.9 / 0.79 | 10.2 / 1.01 |  | 6.8 / 1.01 |
| Machiavellianism | 34.1 / 0.00 | 9.8 / 0.88 | 16.2 / 1.31 | 15.1 / 1.30 | 13.2 / 0.82 | 12.2 / 0.92 | 14.8 / 1.00 | 9.7 / 1.10 | 17.2 / 1.37 | 8.4 / 0.99 |
| Distress | 33.9 / 0.00 | 6.5 / 0.88 | 13.5 / 1.25 | 14.3 / 1.26 | 6.6 / 0.90 | 5.9 / 0.92 | 17.2 / 0.83 | 11.2 / 1.03 | 15.2 / 1.30 | 5.3 / 0.99 |
| Temperament | 21.5 / 0.00 | 12.3 / 0.69 | 12.9 / 1.30 | 13.9 / 1.38 | 9.4 / 0.85 | 10.2 / 0.71 | 13.2 / 0.79 | 10.2 / 1.18 |  | 7.1 / 0.75 |
| Nonverbal behavior | 21.0 / 0.00 | 9.2 / 0.86 | 20.9 / 1.66 | 18.8 / 1.60 | 6.9 / 0.86 | 6.2 / 0.84 | 11.6 / 1.04 | 12.0 / 1.37 | 22.2 / 1.71 | 4.7 / 0.81 |
| General Social Survey | 25.3 / 0.00 | 13.5 / 0.59 | 10.6 / 1.11 | 11.1 / 1.11 | 14.1 / 0.60 | 14.0 / 0.60 | 8.9 / 0.87 | 5.9 / 1.08 |  | 10.6 / 0.71 |
| World Values Survey | 25.2 / 0.00 | 13.1 / 0.53 | 14.1 / 1.23 | 11.6 / 1.13 | 13.0 / 0.52 | 12.2 / 0.56 | 11.7 / 0.73 | 8.3 / 1.08 |  | 9.5 / 0.77 |

F1
| Survey | Test | Gain | 95% CI | Holm p |
|---|---|---|---|---|
| Nerdiness | proseall minus prose12 | -0.9 | -2.4 to +0.7 | 1.0000 |
| Nerdiness | verbal minus prose12 | -0.7 | -2.9 to +1.6 | 1.0000 |
| Nerdiness | numeric minus prose12 | +4.0 | +1.8 to +6.1 | 0.0060 |
| Vocational interests | proseall minus prose12 | +4.9 | +3.0 to +6.8 | 0.0000 |
| Vocational interests | verbal minus prose12 | +6.2 | +3.8 to +8.6 | 0.0000 |
| Vocational interests | numeric minus prose12 | +6.9 | +4.6 to +9.3 | 0.0000 |
| Machiavellianism | proseall minus prose12 | -0.2 | -1.2 to +0.8 | 1.0000 |
| Machiavellianism | verbal minus prose12 | -4.4 | -6.8 to -2.0 | 0.0024 |
| Machiavellianism | numeric minus prose12 | -2.9 | -5.0 to -0.7 | 0.0672 |
| Distress | proseall minus prose12 | +1.3 | -0.1 to +2.6 | 0.3948 |
| Distress | verbal minus prose12 | +9.2 | +6.8 to +11.6 | 0.0000 |
| Distress | numeric minus prose12 | +9.4 | +7.2 to +11.8 | 0.0000 |
| Temperament | proseall minus prose12 | -0.7 | -2.8 to +1.5 | 1.0000 |
| Temperament | verbal minus prose12 | +12.8 | +10.1 to +15.4 | 0.0000 |
| Temperament | numeric minus prose12 | +14.7 | +11.9 to +17.6 | 0.0000 |
| Nonverbal behavior | proseall minus prose12 | +2.2 | +0.8 to +3.7 | 0.0144 |
| Nonverbal behavior | verbal minus prose12 | +21.4 | +18.7 to +24.1 | 0.0000 |
| Nonverbal behavior | numeric minus prose12 | +22.0 | +19.4 to +24.7 | 0.0000 |
| General Social Survey | proseall minus prose12 | -1.7 | -3.7 to +0.3 | 0.5390 |
| General Social Survey | verbal minus prose12 | +4.8 | +2.0 to +7.6 | 0.0060 |
| General Social Survey | numeric minus prose12 | +6.1 | +3.3 to +8.8 | 0.0000 |
| World Values Survey | proseall minus prose12 | +3.3 | +1.5 to +5.1 | 0.0024 |
| World Values Survey | verbal minus prose12 | +9.4 | +7.1 to +11.8 | 0.0000 |
| World Values Survey | numeric minus prose12 | +8.4 | +6.1 to +10.8 | 0.0000 |

F2
| Survey | Test | Gain | 95% CI | Holm p |
|---|---|---|---|---|
| Nerdiness | learned minus numeric | +9.8 | +7.6 to +12.0 | 0.0000 |
| Nerdiness | learned minus verbal | +14.5 | +12.1 to +16.8 | 0.0000 |
| Vocational interests | learned minus numeric | +3.5 | +1.6 to +5.5 | 0.0000 |
| Vocational interests | learned minus verbal | +4.3 | +2.2 to +6.2 | 0.0000 |
| Machiavellianism | learned minus numeric | +7.4 | +5.2 to +9.4 | 0.0000 |
| Machiavellianism | learned minus verbal | +8.9 | +6.6 to +11.2 | 0.0000 |
| Distress | learned minus numeric | -0.2 | -1.8 to +1.5 | 1.0000 |
| Distress | learned minus verbal | +0.0 | -1.7 to +1.8 | 1.0000 |
| Temperament | learned minus numeric | -0.3 | -2.4 to +1.7 | 1.0000 |
| Temperament | learned minus verbal | +1.6 | -0.7 to +3.9 | 0.6696 |
| Nonverbal behavior | learned minus numeric | +2.4 | +0.6 to +4.2 | 0.0456 |
| Nonverbal behavior | learned minus verbal | +3.1 | +1.2 to +5.0 | 0.0084 |
| General Social Survey | learned minus numeric | +2.7 | +0.3 to +5.1 | 0.1560 |
| General Social Survey | learned minus verbal | +3.9 | +1.6 to +6.3 | 0.0080 |
| World Values Survey | learned minus numeric | +4.4 | +2.6 to +6.1 | 0.0000 |
| World Values Survey | learned minus verbal | +3.4 | +1.8 to +5.1 | 0.0000 |

F3
| Survey | Test | Gain | 95% CI | Holm p |
|---|---|---|---|---|
| Nerdiness | prose12 damped minus prose12 | -5.7 | -7.9 to -3.5 | 0.0000 |
| Nerdiness | proseall damped minus proseall | -3.2 | -5.0 to -1.5 | 0.0124 |
| Nerdiness | verbal damped minus verbal | +0.0 | -0.1 to +0.2 | 1.0000 |
| Nerdiness | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Nerdiness | moderate minus prose12 | -8.8 | -11.1 to -6.6 | 0.0000 |
| Nerdiness | elicit minus prose12 | -0.9 | -2.5 to +0.8 | 1.0000 |
| Vocational interests | prose12 damped minus prose12 | -2.7 | -4.8 to -0.7 | 0.1728 |
| Vocational interests | proseall damped minus proseall | -5.8 | -8.4 to -3.2 | 0.0000 |
| Vocational interests | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| Vocational interests | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Vocational interests | moderate minus prose12 | -3.8 | -6.0 to -1.7 | 0.0174 |
| Vocational interests | elicit minus prose12 | +0.2 | -1.6 to +2.0 | 1.0000 |
| Machiavellianism | prose12 damped minus prose12 | -10.4 | -13.1 to -7.8 | 0.0000 |
| Machiavellianism | proseall damped minus proseall | -9.2 | -11.8 to -6.6 | 0.0000 |
| Machiavellianism | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| Machiavellianism | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Machiavellianism | moderate minus prose12 | -5.6 | -7.6 to -3.6 | 0.0000 |
| Machiavellianism | elicit minus prose12 | +1.9 | +0.6 to +3.2 | 0.0900 |
| Distress | prose12 damped minus prose12 | -4.0 | -6.6 to -1.4 | 0.0780 |
| Distress | proseall damped minus proseall | -6.4 | -9.3 to -3.6 | 0.0000 |
| Distress | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| Distress | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Distress | moderate minus prose12 | -5.6 | -7.7 to -3.4 | 0.0000 |
| Distress | elicit minus prose12 | -2.7 | -4.4 to -0.9 | 0.0702 |
| Temperament | prose12 damped minus prose12 | +9.5 | +6.9 to +12.0 | 0.0000 |
| Temperament | proseall damped minus proseall | +11.6 | +8.8 to +14.4 | 0.0000 |
| Temperament | verbal damped minus verbal | +0.1 | -0.2 to +0.4 | 1.0000 |
| Temperament | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Temperament | moderate minus prose12 | +6.4 | +3.9 to +8.8 | 0.0000 |
| Temperament | elicit minus prose12 | +6.6 | +4.6 to +8.8 | 0.0000 |
| Nonverbal behavior | prose12 damped minus prose12 | +18.7 | +15.7 to +21.7 | 0.0000 |
| Nonverbal behavior | proseall damped minus proseall | +17.0 | +14.1 to +19.9 | 0.0000 |
| Nonverbal behavior | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| Nonverbal behavior | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| Nonverbal behavior | moderate minus prose12 | +11.3 | +8.8 to +13.8 | 0.0000 |
| Nonverbal behavior | elicit minus prose12 | +4.3 | +2.6 to +5.9 | 0.0000 |
| General Social Survey | prose12 damped minus prose12 | -1.5 | -3.1 to +0.2 | 1.0000 |
| General Social Survey | proseall damped minus proseall | -0.3 | -2.0 to +1.5 | 1.0000 |
| General Social Survey | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| General Social Survey | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| General Social Survey | moderate minus prose12 | +3.5 | +1.4 to +5.6 | 0.0560 |
| General Social Survey | elicit minus prose12 | +4.5 | +2.3 to +6.7 | 0.0124 |
| World Values Survey | prose12 damped minus prose12 | -1.2 | -3.4 to +1.0 | 1.0000 |
| World Values Survey | proseall damped minus proseall | -1.0 | -3.0 to +1.1 | 1.0000 |
| World Values Survey | verbal damped minus verbal | +0.0 | +0.0 to +0.0 | 1.0000 |
| World Values Survey | numeric damped minus numeric | +0.0 | +0.0 to +0.0 | 1.0000 |
| World Values Survey | moderate minus prose12 | +2.6 | +0.7 to +4.6 | 0.1840 |
| World Values Survey | elicit minus prose12 | +4.1 | +2.4 to +5.9 | 0.0000 |

F4
| Survey | Test | Gain | 95% CI | Holm p |
|---|---|---|---|---|
| Nerdiness | think minus prose12 | +1.3 | +0.1 to +2.6 | 0.1122 |
| Machiavellianism | think minus prose12 | +0.3 | -0.5 to +1.1 | 0.5272 |
| Distress | think minus prose12 | -0.6 | -1.5 to +0.3 | 0.3932 |
| Nonverbal behavior | think minus prose12 | -1.0 | -1.9 to -0.2 | 0.0776 |

## Exploratory: capacity curve

Accuracy on half B by number of data-learned groups (exploratory; data assignment, most common answer of the group)
| Survey | k=1 | k=2 | k=3 | k=4 | k=6 | k=9 | k=14 | k=27 | k=54 | Type vector | Groups needed to match the type vector |
|---|---|---|---|---|---|---|---|---|---|---|---|
| npas | 40.5 | 41.8 | 41.8 | 43.0 | 44.4 | 44.5 | 45.9 | 44.8 | 43.5 | 38.0 | 1 |
| riasec | 32.7 | 36.2 | 37.8 | 38.3 | 39.4 | 40.6 | 42.6 | 42.6 | 43.5 | 37.5 | 3 |
| mach | 35.5 | 42.2 | 43.1 | 43.5 | 43.5 | 44.1 | 43.6 | 42.4 | 41.9 | 37.7 | 2 |
| dass | 34.0 | 46.3 | 48.1 | 49.0 | 52.9 | 52.1 | 52.7 | 53.8 | 54.7 | 51.6 | 6 |
| fti | 44.8 | 46.3 | 46.6 | 47.6 | 47.4 | 47.8 | 48.2 | 49.6 | 49.5 | 46.8 | 4 |
| nis | 35.9 | 44.4 | 46.6 | 48.0 | 47.8 | 49.8 | 49.1 | 49.0 | 49.2 | 40.8 | 2 |
| gss2022 | 50.8 | 52.2 | 52.3 | 53.5 | 55.1 | 53.2 | 54.8 | 55.0 | 53.5 | 51.2 | 2 |
| wvs7 | 41.6 | 42.4 | 44.7 | 44.5 | 45.6 | 45.4 | 45.2 | 46.4 | 45.5 | 40.1 | 1 |

## Exploratory: sketch audit

Exploratory audit of the sketch condition: items where the model moves a described group the wrong way (groups departing > 0.3 sd)

**Nerdiness** (28% of group-item departures go the wrong way)
- 47% wrong of 15 groups: "I like to play RPGs. (Ex. D&D)" (humans higher but model lower: 7; humans lower but model higher: 0)
- 45% wrong of 20 groups: "I watch science related shows." (humans higher but model lower: 9; humans lower but model higher: 0)
- 43% wrong of 14 groups: "I can be socially awkward at times." (humans higher but model lower: 6; humans lower but model higher: 0)

**Vocational interests** (23% of group-item departures go the wrong way)
- 42% wrong of 19 groups: "Manage a department within a large company" (humans higher but model lower: 7; humans lower but model higher: 1)
- 41% wrong of 27 groups: "Do volunteer work at a non-profit organization" (humans higher but model lower: 11; humans lower but model higher: 0)
- 38% wrong of 21 groups: "Teach children how to read" (humans higher but model lower: 7; humans lower but model higher: 1)

**Machiavellianism** (19% of group-item departures go the wrong way)
- 59% wrong of 27 groups: "People suffering from incurable diseases should have the choice of being put painlessly to death." (humans higher but model lower: 16; humans lower but model higher: 0)
- 30% wrong of 27 groups: "It is possible to be good in all respects." (humans higher but model lower: 4; humans lower but model higher: 4)
- 30% wrong of 27 groups: "It is wise to flatter important people." (humans higher but model lower: 6; humans lower but model higher: 2)

**Distress** (12% of group-item departures go the wrong way)
- 24% wrong of 17 groups: "I perspired noticeably (eg, hands sweaty) in the absence of high temperatures or physical exertion." (humans higher but model lower: 0; humans lower but model higher: 4)
- 23% wrong of 26 groups: "I found it difficult to work up the initiative to do things." (humans higher but model lower: 4; humans lower but model higher: 2)
- 22% wrong of 27 groups: "I just couldn't seem to get going." (humans higher but model lower: 4; humans lower but model higher: 2)

**Temperament** (19% of group-item departures go the wrong way)
- 40% wrong of 15 groups: "I vividly imagine both wonderful and horrible things happening to me." (humans higher but model lower: 6; humans lower but model higher: 0)
- 37% wrong of 27 groups: "I do things on the spur of the moment." (humans higher but model lower: 10; humans lower but model higher: 0)
- 36% wrong of 14 groups: "I often find myself getting lost in my thoughts during the day." (humans higher but model lower: 5; humans lower but model higher: 0)

**Nonverbal behavior** (8% of group-item departures go the wrong way)
- 22% wrong of 27 groups: "I frown while talking to people." (humans higher but model lower: 6; humans lower but model higher: 0)
- 19% wrong of 27 groups: "I have a tense body position while talking to people." (humans higher but model lower: 5; humans lower but model higher: 0)
- 19% wrong of 27 groups: "I use a monotone or dull voice while talking to people." (humans higher but model lower: 2; humans lower but model higher: 3)

**General Social Survey** (22% of group-item departures go the wrong way)
- 44% wrong of 27 groups: "Is life exciting or dull (1=exciting / 2=routine / 3=dull)" (humans higher but model lower: 12; humans lower but model higher: 0)
- 42% wrong of 19 groups: "How often do you: spend evening with neighbor? (1=almost daily / 2=once or twice a week / 3=several times a mo" (humans higher but model lower: 3; humans lower but model higher: 5)
- 41% wrong of 27 groups: "Are we spending too much money, too little money, or about the right amount on: highways and bridges? (1=too l" (humans higher but model lower: 6; humans lower but model higher: 5)

**World Values Survey** (25% of group-item departures go the wrong way)
- 67% wrong of 27 groups: "How good is this way of governing the country: Having experts, not government, make decisions according to wh " (humans higher but model lower: 2; humans lower but model higher: 16)
- 54% wrong of 26 groups: "Interest in politics (1=Very interested / 2=Somewhat interested / 3=Not very interested / 4=Not at all interes" (humans higher but model lower: 13; humans lower but model higher: 1)
- 50% wrong of 26 groups: "How good is this way of governing the country: Having a strong leader who does not have to bother with parlia " (humans higher but model lower: 1; humans lower but model higher: 12)

Overall: 20% of 7342 group-item departures go the wrong way.
