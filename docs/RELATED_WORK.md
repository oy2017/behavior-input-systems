# Related work for the round-trip paper

Checked 2026-11-08. Abstracts and HTML versions read; full PDFs not yet. Each entry ends with how the round-trip study
differs. Searches were not exhaustive; re-check before submission.

## Closest

**Jia, Chen, Sharma, Diaz-Rodriguez. When Can Digital Personas Reliably Approximate Human Survey Findings? NeurIPS
2026 (arXiv 2605.10659).** LISS panel, 500 respondents per task, 2,923 questions, GPT-5.4 / Gemini 3 Flash / Claude
Haiku 4.5. Four persona architectures: background variables only; background plus a structured profile written by
GPT-5.4 from prior answers; profile plus retrieved prior rows (lexical or semantic). Evaluated at question, respondent,
distribution, equity and clustering level. Findings: distributions improve (question JSD 0.53 to 0.30), individuals
barely (exact match 0.48 to 0.53), clustering recovery weak (ARI near 0 on the core task), and persona answers compress
human variation (variance ratio 0.6 to 0.75). Baselines: no-context LLM only; modal-answer baselines were excluded
because they need held-out human answers. No remedy tested.
*Difference:* they describe individuals and find compression; we describe data-learned groups, compare against what the
same data predicts (the group's own answers), and find exaggeration. We test remedies.

**Lee, Łajewska, Perelli, Mansour. Data-Driven Personas for Survey Simulation: Insights into Simulation Alignment Across
Data-Access Regimes. REALM at EMNLP 2026 (arXiv 2610.05828).** Personas are second-person texts written by Claude 3.7
Sonnet from behavioral records (movie reviews, shopping, other surveys, or 20 to 80 percent of the target survey).
Target: demographic-group distributions on GSS, OpinionQA, SocSci210, measured by total variation and Wasserstein
distance. Findings: out-of-domain personas rarely beat demographics only; alignment improves with more in-domain
history (GSS TVD 0.184 at 20 percent to 0.163 at 80 percent), but a single-attribute demographic baseline is close
(0.153 to 0.149). Asking the model for a verbalized distribution beats single answers aggregated, because single
answers collapse toward dominant options. No non-LLM baseline that uses the same history.
*Difference:* their unit is a demographic group; ours is a behavioral type with a known behavior. Our "elicit" fix is
their verbalized-distribution design applied to types, and should be credited to them.

**Chae, Choi, Lee, Im. Cultural Divergence Preservation: Diagnosing Flattening and Caricature in LLM-Simulated Survey
Populations. PANDORA at EMNLP 2026 (arXiv 2609.29928).** Defines flattening and caricature at the country level as
reduced or increased cross-country divergence relative to humans; four LLMs, three persona methods, WVS and Big Five.
The method favored by distribution-matching metrics flattens most. No remedies, nothing below country level.
*Difference:* we measure exaggeration for each type against its own members, at the item level.

**Abels, Fernandez Domingos, Shah, Lenaerts. Improving Cross-Cultural Survey Simulation with Calibrated Value Personas.
VALE at IJCAI-ECAI 2026 (arXiv 2605.16193).** Personas built from answers on core value dimensions; a calibration step
improves response diversity. Details of the calibration not yet read.
*Difference:* their calibration widens under-dispersed output; our damping narrows exaggerated output.

## Background to cite

- Argyle et al. 2023, silicon samples. Santurkar et al. 2023, OpinionQA. Bisbee et al. 2024, synthetic replacements and
  their perils. Dominguez-Olmedo et al. 2024, questioning LLM survey responses.
- Park et al. 2024, generative agent simulations of 1,000 people: interviews beat demographics.
- Toubia et al. 2025, Twin-2K-500; Peng et al. 2025, mega-study of digital twins: good at means, weak on individuals.
- Hu and Collier 2024, quantifying the persona effect: persona variables explain little variance.
- Cheng, Durmus, Jurafsky 2023, CoMPosT: caricature in persona simulation. Wang et al. 2024, LLMs cannot portray
  identity groups. EMNLP 2025 "Who Holds the Pen?": caricature as individuation plus exaggeration.
- Jackson, Manning, Xie, Yuan, Mei 2026, type vectors (arXiv 2608.18265). Wang, Wu, Zeevi, ICML 2026, personas as latent
  classes. Kim and Lee 2023, AI-augmented surveys (fine-tuning predicts unasked items).
- Data-driven personas in HCI, the segment-then-describe pipeline the main experiment diagnoses. To verify before
  submission: An, Kwak, Salminen, Jung, Jansen (2018), "Imaginary People Representing Real Numbers", ACM Transactions
  on the Web (clusters users from behavioral data and generates a persona per cluster); Salminen, Guan, Jung, Jansen
  (2021), "A Survey of 15 Years of Data-Driven Persona Development", International Journal of Human-Computer
  Interaction; Jansen, Salminen, Jung, Guan (2021), Data-Driven Personas, Morgan and Claypool.
- "The Prompt Makes the Person(a)" (arXiv 2507.16076): persona prompt wording changes stereotyping and alignment.
- "Assessing the Reliability of Persona-Conditioned LLMs as Synthetic Survey Respondents" (arXiv 2602.18462): aggregate
  fidelity can hold while subgroup claims fail.

## What this leaves open, and what the round trip adds

1. No prior study scores a persona against the known behavior of the group it summarizes, with a same-capacity data
   baseline. Prior baselines are no-context or demographics-only.
2. No prior study varies description richness from sketch to full profile while holding the group fixed and leaving the
   predicted item out.
3. Exaggeration has been measured for text and for countries, not for behavioral types against their own members.
4. Remedies have been proposed separately (verbalized distributions; calibration for diversity) but not compared under
   pre-committed criteria.
