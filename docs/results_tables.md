# Result tables (generated; model = gemini-3.5-flash, thinking off)

## Track A: survey item prediction, 997 matched subject-item pairs

| Condition | LLM acc | LLM MAE | LLM W(item) | sd ratio | Supervised ceiling acc | Ceiling W(item) |
|---|---|---|---|---|---|---|
| none | 0.292 | 1.080 | 1.053 | 0.91 | (per-item mode 0.313) | - |
| demographics | 0.309 | 1.001 | 0.883 | 0.82 | 0.356 | 0.668 |
| big_five | 0.408 | 0.804 | 0.476 | 0.99 | 0.493 | 0.326 |
| demographics+big_five | 0.426 | 0.754 | 0.454 | 0.96 | 0.508 | 0.317 |
| history | 0.484 | 0.741 | 0.363 | 1.00 | 0.527 | 0.334 |
| demographics+history | 0.479 | 0.742 | 0.352 | 0.99 | 0.529 | 0.317 |
| type_table_econ | 0.339 | 0.952 | 0.693 | 0.87 | - | - |
| type_vector_econ | 0.330 | 0.962 | 0.688 | 0.87 | - | - |
| history+type_vector_econ | 0.461 | 0.758 | 0.378 | 0.99 | - | - |
| type_table_bigfive | 0.376 | 0.900 | 0.582 | 0.92 | - | - |
| type_vector_bigfive | 0.372 | 0.924 | 0.558 | 0.94 | - | - |
| history+type_vector_bigfive | 0.456 | 0.740 | 0.393 | 0.94 | - | - |

## Track B: held-out game prediction, 6,262 records, per game

| Game | n | none MAE / W | history MAE / W | type_table MAE / W | type_vector MAE / W | type_vector_x5 MAE / W | history+type_vector MAE / W | history+type_vector_x5 MAE / W | HistGBT MAE | W floor |
|---|---|---|---|---|---|---|---|---|---|---|
| dictator | 750 | 24.7 / 24.6 | 24.2 / 12.8 | 22.5 / 3.2 | 23.9 / 6.1 | 24.0 / 6.1 | 23.8 / 6.9 | 24.2 / 6.9 | 18.5 | 0.85 |
| ultimatum_proposer | 750 | 14.4 / 12.9 | 12.7 / 7.2 | 14.6 / 6.8 | 14.6 / 4.8 | 14.6 / 4.8 | 12.8 / 5.5 | 12.9 / 5.5 | 13.4 | 0.87 |
| ultimatum_responder | 750 | 33.7 / 33.7 | 18.1 / 11.5 | 26.2 / 23.6 | 27.8 / 24.9 | 27.9 / 24.9 | 22.8 / 18.1 | 23.2 / 18.1 | 14.0 | 0.82 |
| trust_investor | 750 | 53.9 / 49.2 | 40.6 / 16.5 | 37.8 / 9.6 | 38.5 / 4.1 | 38.3 / 4.1 | 38.3 / 4.1 | 38.3 / 4.1 | 32.6 | 1.29 |
| trust_banker | 262 | 28.3 / 9.3 | 25.8 / 11.0 | 23.4 / 7.7 | 26.9 / 10.3 | 26.2 / 10.3 | 26.3 / 10.4 | 26.1 / 10.4 | 20.5 | 1.66 |
| public_goods | 750 | 51.1 / 49.9 | 37.7 / 18.7 | 33.0 / 3.7 | 38.1 / 10.3 | 37.4 / 10.3 | 36.4 / 10.6 | 36.8 / 10.6 | 26.3 | 1.32 |
| bomb | 750 | 17.8 / 17.7 | 17.8 / 17.6 | 24.3 / 6.8 | 32.7 / 9.2 | 32.7 / 9.2 | 33.3 / 12.9 | 33.1 / 12.9 | 19.4 | 1.08 |
| guessing | 750 | 23.5 / 21.4 | 23.3 / 20.6 | 21.2 / 16.6 | 21.3 / 11.5 | 21.4 / 11.5 | 21.4 / 10.1 | 21.3 / 10.1 | 20.0 | 0.99 |
| push_pull (categorical) | 750 | acc 0.436 | acc 0.435 | acc 0.529 | acc 0.540 | acc 0.543 | acc 0.535 | acc 0.539 | - | - |

### Track B means over the eight numeric games

| Condition | MAE | W | mean sd ratio |
|---|---|---|---|
| none | 30.92 | 27.33 | 0.30 |
| history | 25.03 | 14.48 | 0.65 |
| type_table | 25.37 | 9.74 | 0.70 |
| type_vector | 27.98 | 10.15 | 0.94 |
| type_vector_x5 | 27.81 | 10.15 | 0.94 |
| history+type_vector | 26.87 | 9.83 | 0.96 |
| history+type_vector_x5 | 26.99 | 9.83 | 0.96 |
| HistGBT ceiling | 20.60 | - | - |
