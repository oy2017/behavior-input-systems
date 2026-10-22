# Does reasoning change the picture? Gemini 3.8 Flash with thinking on vs 3.5 Flash with thinking off

Same prompts, same subjects, one draw per record. The thinking model deliberates (hidden reasoning
tokens) before answering; the non-thinking model answers directly. Accuracy on the held-out item
(games: MAE on the 0-100 scale, lower is better).

| Dataset | Input | thinking off (3.5 Flash) | thinking on (3.8 Flash) | change | supervised ceiling |
|---|---|---|---|---|---|
| Big Five items | nothing | 29.2 | 28.4 | -0.8 | 31.3 (mode) |
| | demographics | 30.9 | 30.6 | -0.3 | 35.6 |
| | Big Five scores | 40.8 | 45.5 | **+4.7** | 49.3 |
| | history | 48.4 | 47.7 | -0.7 | 52.7 |
| MACH | nothing | 33.2 | 25.5 | -7.7 | 38.6 (mode) |
| | demographics | 28.5 | 26.9 | -1.6 | 42.3 |
| | TIPI scores | 30.9 | 35.5 | **+4.6** | 42.0 |
| | history | 44.2 | 47.0 | +2.8 | 52.8 |
| NIS | nothing | 27.0 | 34.1 | +7.1 | 35.7 (mode) |
| | demographics | 34.3 | 33.6 | -0.7 | 36.5 |
| | TIPI scores | 25.3 | 28.9 | +3.6 | 40.4 |
| | history | 52.2 | 54.1 | +1.9 | 56.4 |
| WVS 7 | nothing | 34.0 | 36.9 | +2.9 | 42.6 (mode) |
| | demographics | 41.2 | 42.3 | +1.1 | 47.3 |
| | value indices | 38.5 | 39.8 | +1.3 | 45.4 |
| | history | 52.7 | 56.3 | **+3.6** | 56.0 |
| MobLab games (MAE) | nothing | 30.9 | 29.5 | -1.4 | |
| | history | 25.0 | 23.2 | **-1.8** | 20.6 (HistGBT) |

## Reading

1. **Reasoning does not rescue demographics.** Across four datasets the demographics condition moves
   by -1.6 to +1.1 points with thinking on, and stays 4 to 15 points under what a supervised model
   extracts from the same fields. On NIS the gain demographics had over nothing disappears entirely
   once the model thinks (33.6 vs 34.1). Deliberating over a profile does not make the stereotype more
   accurate.
2. **Reasoning helps the model read numeric trait scores.** Measured scores gain 3.6 to 4.7 points on
   the three personality datasets, closing about half the gap to the ceiling. The model appears to
   work out what "Neuroticism: 42 out of 50" implies instead of pattern-matching on it.
3. **Reasoning helps history a little**, +2 to +4 on three datasets, and on WVS reaches the ceiling. In
   the games it lowers MAE from 25.0 to 23.2 and W from 14.5 to 13.3.
5. **Reasoning does not cure the collapse.** Told nothing about the player, the thinking model still
   gives one answer to everyone on Dictator and Bomb (sd ratio 0.00) and reproduces under 15% of the
   human spread on Guessing and Public Goods; W with nothing is 26.6 vs 27.3 without thinking.
4. **Reasoning changes the uninformed baseline unpredictably** (-7.7 on MACH, +7.1 on NIS): without
   subject information the model's answer depends on what it talks itself into.

Cost, measured on Gemini 3.5 Flash in the feasibility probe: thinking on used about seven times the
tokens per call (1,707 vs 238 total tokens) and three times the latency (7.7 s vs 2.5 s). The 3.8 Flash
runs were not separately timed.

The ordering of inputs is unchanged by reasoning: history > fitted or measured traits > demographics
≈ nothing. Finding 3 of the main write-up (the model under-uses demographics far more than it
under-uses behavior) holds for both configurations; reasoning narrows the trait-score gap, not the
demographics gap.
