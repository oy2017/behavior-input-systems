# Survey suite results (generated; model = gemini-3.5-flash, thinking off; 1,000 records per dataset)

Condition keys: `type_table` = type-based prediction from the best-fitting type vector (Jackson et al. 2026); `type_vector` = best-fitting type vector used as the system prompt; `traits` = measured self-report scores; `history` = the subject's other answers.

## Accuracy (exact answer)

| dataset | none | demographics | traits | history | demographics+traits | demographics+history | type_table | type_vector | history+type_vector |
|---|---|---|---|---|---|---|---|---|---|
| dass | 0.255 | 0.301 | 0.401 | 0.529 | 0.412 | 0.537 | 0.482 | 0.484 | 0.535 |
| fti | 0.407 | 0.422 | 0.416 | 0.557 | 0.443 | 0.574 | 0.465 | 0.435 | 0.549 |
| gss2022 | 0.483 | 0.479 | 0.465 | 0.561 | 0.482 | 0.567 | 0.477 | 0.501 | 0.552 |
| mach | 0.332 | 0.285 | 0.309 | 0.442 | 0.314 | 0.451 | 0.388 | 0.380 | 0.421 |
| nis | 0.270 | 0.343 | 0.253 | 0.522 | 0.271 | 0.536 | 0.392 | 0.409 | 0.539 |
| npas | 0.344 | 0.273 | 0.330 | 0.377 | 0.276 | 0.354 | 0.294 | 0.289 | 0.357 |
| riasec | 0.225 | 0.275 | 0.261 | 0.497 | 0.282 | 0.505 | 0.305 | 0.309 | 0.483 |
| socsci210 | 0.262 | 0.274 |  | 0.425 |  | 0.421 |  |  |  |
| wvs7 | 0.347 | 0.418 | 0.396 | 0.532 | 0.426 | 0.532 | 0.363 | 0.384 | 0.529 |

## W per target item (0-100 normalised; lower is better)

| dataset | none | demographics | traits | history | demographics+traits | demographics+history | type_table | type_vector | history+type_vector |
|---|---|---|---|---|---|---|---|---|---|
| dass | 46.51 | 34.52 | 12.55 | 10.24 | 13.26 | 9.92 | 9.95 | 10.76 | 10.90 |
| fti | 22.40 | 17.93 | 11.58 | 8.61 | 10.56 | 9.25 | 14.40 | 14.78 | 10.01 |
| gss2022 | 23.89 | 15.56 | 14.17 | 14.59 | 14.15 | 13.60 | 17.90 | 15.77 | 13.68 |
| mach | 27.72 | 18.51 | 15.26 | 10.06 | 15.89 | 9.92 | 13.07 | 15.58 | 9.78 |
| nis | 27.16 | 18.32 | 21.29 | 7.21 | 19.92 | 6.91 | 12.08 | 10.83 | 7.14 |
| npas | 28.43 | 20.55 | 18.08 | 16.38 | 16.06 | 16.49 | 19.75 | 18.67 | 15.65 |
| riasec | 36.40 | 17.11 | 18.05 | 9.81 | 15.58 | 9.68 | 14.39 | 14.47 | 8.58 |
| socsci210 | 12.05 | 10.59 |  | 6.07 |  | 6.22 |  |  |  |
| wvs7 | 24.06 | 16.44 | 17.43 | 10.48 | 15.84 | 11.18 | 22.45 | 18.36 | 10.67 |

## sd ratio (1 = human spread)

| dataset | none | demographics | traits | history | demographics+traits | demographics+history | type_table | type_vector | history+type_vector |
|---|---|---|---|---|---|---|---|---|---|
| dass | 0.00 | 0.46 | 0.93 | 0.96 | 0.93 | 0.98 | 0.90 | 0.89 | 0.97 |
| fti | 0.53 | 0.65 | 1.07 | 0.90 | 0.99 | 0.87 | 0.72 | 0.80 | 0.86 |
| gss2022 | 0.88 | 0.96 | 0.95 | 0.99 | 0.96 | 1.00 | 0.98 | 1.01 | 1.02 |
| mach | 0.98 | 0.82 | 0.88 | 0.94 | 0.86 | 0.94 | 0.92 | 0.97 | 0.94 |
| nis | 1.13 | 0.87 | 1.07 | 1.03 | 1.02 | 1.02 | 0.89 | 0.90 | 1.00 |
| npas | 0.38 | 0.57 | 0.67 | 0.77 | 0.67 | 0.81 | 0.64 | 0.65 | 0.75 |
| riasec | 0.75 | 0.80 | 0.83 | 1.08 | 0.82 | 1.06 | 0.78 | 0.81 | 1.06 |
| socsci210 | 0.97 | 0.90 |  | 1.01 |  | 0.97 |  |  |  |
| wvs7 | 0.78 | 0.88 | 0.83 | 0.98 | 0.88 | 0.99 | 0.84 | 0.85 | 0.97 |

## Supervised ceiling: accuracy (pooled HistGBT trained on 4,000 to 5,000 other respondents with every item as a target; SocSci210 uses 5-fold CV on the 1,000 records)

| dataset | none | demographics | traits | history | demographics+traits | demographics+history |
|---|---|---|---|---|---|---|
| dass | 0.338 | 0.357 | 0.428 | 0.564 | 0.444 | 0.572 |
| fti | 0.450 | 0.475 | 0.528 | 0.597 | 0.549 | 0.600 |
| gss2022 | 0.503 | 0.523 | 0.520 | 0.592 | 0.534 | 0.593 |
| mach | 0.386 | 0.423 | 0.420 | 0.528 | 0.444 | 0.527 |
| nis | 0.357 | 0.365 | 0.404 | 0.564 | 0.409 | 0.560 |
| npas | 0.401 | 0.413 | 0.427 | 0.522 | 0.437 | 0.516 |
| riasec | 0.313 | 0.367 | 0.351 | 0.531 | 0.365 | 0.524 |
| socsci210 | 0.155 | 0.191 |  | 0.333 |  | 0.317 |
| wvs7 | 0.426 | 0.473 | 0.454 | 0.560 | 0.481 | 0.573 |
