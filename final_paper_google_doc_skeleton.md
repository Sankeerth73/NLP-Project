# Prompt-Based CEFR-Controlled Text Simplification with a Small Open-Weight LLM

Authors: Jinyu Chen, Sankeerth Adisha, David Kim, Shaohua Liu  
Course: CS6120 Natural Language Processing  
Target format: ACL-style long paper, 8 pages main content, references excluded

---

## Google Docs / ACL Formatting Setup

Before writing, set the Google Doc format as closely as possible to ACL:

- Page size: A4
- Margins: 2.5 cm on all sides
- Columns: two columns for the main paper body
- Font: Times New Roman
- Main text: 11 pt, single spaced
- Title: 15 pt, bold, centered
- Authors: 12 pt, bold, centered
- Section titles: 12 pt, bold, numbered
- Subsection titles: 11 pt, bold, numbered
- Abstract heading: 12 pt, bold, centered
- Abstract text: 10 pt
- Captions: 10 pt
- References: 10 pt

ACL constraints to remember:

- Main paper content limit: 8 pages.
- References do not count toward the 8 pages.
- Main-text figures and tables do count toward the 8 pages.
- Abstract must be no more than 200 words.
- Include a section titled "Limitations" after Conclusion and before References.
- Keep the main paper self-contained; do not put core results only in the appendix.

---

# Abstract

[Owner: Member D. Write this last. Target: 150-180 words.]

[Replace this paragraph with a concise summary of the task, method, data, evaluation, and main finding. Mention TSAR 2025, CEFR-controlled simplification, Qwen/Qwen2.5-0.5B-Instruct, zero-shot, three-shot, self-refinement, CEFR accuracy/RMSE, MeaningBERT, and the core result that three-shot prompting was stronger than self-refinement in this setting.]

---

# 1 Introduction

[Owner: Member D. Target: about 0.75 page.]

Text simplification aims to rewrite text so that it is easier to read while preserving the original meaning. This problem is important for language learners, accessibility technologies, and readers who need text at a specific proficiency level. Recent shared tasks have moved beyond generic simplification toward readability-controlled simplification, where systems must produce output matching a requested level such as A2 or B1 on the Common European Framework of Reference for Languages (CEFR).

[Replace/extend with context from prior work: traditional simplification, controllable simplification, LLM prompting, and TSAR 2025.]

However, controlling readability remains difficult because a system must satisfy two competing goals: simplify enough to match the target level while preserving the source meaning. Large proprietary models and complex multi-stage systems have shown promising results, but it is less clear whether very small open-weight instruction models can reliably perform CEFR-controlled simplification through prompting alone.

In this paper, we study prompt-based CEFR-controlled text simplification using a small open-weight language model. We compare three inference-only conditions: direct zero-shot prompting, target-matched three-shot prompting, and CEFR-feedback self-refinement. Our experiments use the TSAR 2025 English readability-controlled simplification data and evaluate both target-level control and semantic preservation.

Our contributions are:

1. We provide a reproducible evaluation of zero-shot, three-shot, and self-refinement prompting for CEFR-controlled simplification with a small open-weight model.
2. We measure the tradeoff between readability control and semantic preservation using CEFR prediction and MeaningBERT metrics.
3. We show that, in our setting, three-shot prompting improves over zero-shot, while CEFR-feedback self-refinement performs close to zero-shot despite adding revision steps.

---

# 2 Task and Problem

[Owner: Member A. Target: about 0.75 page.]

## 2.1 Task Definition

[Replace with a precise description of the TSAR 2025 task.]

Given an English source paragraph and a target CEFR level, the system must produce a simplified paragraph that preserves the source meaning while matching the requested readability level. In our experiments, the target levels are A2 and B1.

Input:

- Source paragraph
- Target CEFR level: A2 or B1

Output:

- Simplified paragraph at the requested target level

## 2.2 Why the Problem Is Interesting

[Member A: explain why this is not just generic simplification.]

The task is challenging because simpler text is not always better: output that is too simple may omit essential information, while output that preserves every detail may remain too complex. CEFR-controlled simplification therefore requires balancing readability, adequacy, fluency, and discourse-level meaning preservation.

## 2.3 Research Questions

We ask:

RQ1: How do zero-shot, three-shot, and CEFR-feedback self-refinement prompting affect target-level control?

RQ2: What happens to semantic preservation when target-level control changes?

RQ3: Are A2 and B1 targets equally difficult for a small open-weight instruction model?

---

# 3 Related Work

[Owner: Member D, with citations contributed by all members. Target: about 1.25 pages.]

## 3.1 Text Simplification Data and Systems

[Replace with synthesized discussion. Do not write one paragraph per paper. Discuss SARI, TurkCorpus, ASSET, ACCESS, MUSS, and neural simplification baselines where relevant.]

## 3.2 Controllable and CEFR-Based Simplification

[Discuss controllable simplification and CEFR/readability labels. Connect this directly to TSAR 2025.]

## 3.3 LLM Prompting and Iterative Refinement

[Discuss zero-shot prompting, few-shot prompting, reranking, feedback loops, and multi-agent/self-refinement systems. Explain how your work is narrower: a controlled comparison using one small open-weight model.]

## 3.4 Evaluation of Simplification

[Discuss why overlap metrics alone are insufficient. Mention CEFR prediction, MeaningBERT, SARI/LENS if used or discussed, and human evaluation limitations.]

Transition sentence:

Prior work suggests that examples, reranking, and feedback can improve simplification, but it remains unclear whether a lightweight CEFR-feedback loop helps a very small open-weight model on paragraph-level CEFR-controlled simplification.

---

# 4 Data

[Owner: Member A. Target: about 0.75 page.]

## 4.1 Dataset

[Replace with exact dataset details from member_A_deliverables.]

We use the pinned TSAR 2025 English readability-controlled simplification release prepared in our data pipeline. The evaluated release contains 100 test source texts and 200 target requests, with one A2 and one B1 request per source. We preserve the distinction between source text, target level, and reference simplifications to avoid reference leakage during generation.

## 4.2 Split and Leakage Policy

[Member A: describe generation_inputs.jsonl and few_shot_pool.jsonl. Emphasize that test references were not available to the generation pipeline.]

## 4.3 Dataset Statistics

[Insert Table 1 here. Keep compact.]

Table 1: Dataset statistics for the TSAR 2025 release used in our experiments.

| Split | Source texts | Target requests | A2 requests | B1 requests | Notes |
|---|---:|---:|---:|---:|---|
| Test | 100 | 200 | 100 | 100 | One A2 and one B1 request per source |

[Replace/add exact mean length, sentence count, source/reference length, compression ratio if available.]

---

# 5 Method

[Owner: Member B. Target: about 1.25 pages.]

## 5.1 Model

We use Qwen/Qwen2.5-0.5B-Instruct as the open-weight instruction model for all generated systems. The model is run with deterministic decoding, no sampling, seed 42, and a maximum generation length of 150 new tokens.

[Member B: add exact manifest details, device, revision, and any prompt-processing rules.]

## 5.2 Zero-Shot Prompting

[Member B: describe direct prompt. Do not paste long prompt unless space allows.]

The zero-shot condition gives the model the source paragraph and target CEFR level, then asks it to return only the simplified paragraph without explanation.

## 5.3 Three-Shot Prompting

[Member B: describe how examples are chosen.]

The three-shot condition adds three target-matched demonstrations selected from the permitted few-shot pool. Demonstrations are selected deterministically and never use test references.

## 5.4 CEFR-Feedback Self-Refinement

[Member B: describe loop clearly.]

Self-refinement starts from a direct draft. A generation-time CEFR critic predicts the draft's level. If the predicted level does not match the requested level, the system asks the model to revise the previous output using the source, target level, predicted level, and revision instruction. The loop stops when the predicted level matches the target or after two revisions.

Important distinction:

The generation-time critic is used only to trigger revisions. Final reported CEFR scores are independently recomputed by the evaluation pipeline.

---

# 6 Evaluation Setup

[Owner: Member C. Target: about 0.75 page.]

## 6.1 Systems Compared

We evaluate five systems:

- Identity baseline
- Human-reference oracle
- Open-model zero-shot
- Open-model three-shot
- Open-model self-refinement

The identity baseline copies the source text and tests whether metrics behave sensibly. The human-reference oracle uses a reference simplification and serves as an upper sanity bound, not as a deployable system.

## 6.2 Metrics

[Member C: define metrics exactly.]

We report:

- CEFR exact accuracy: whether the predicted CEFR level exactly matches the target.
- CEFR RMSE: ordinal CEFR error using A1=1, A2=2, B1=3, B2=4, C1=5, C2=6.
- MeaningBERT source similarity: semantic similarity between source and output.
- MeaningBERT reference similarity: semantic similarity between output and reference.
- Mean revisions: average number of completed revisions for self-refinement.

## 6.3 Uncertainty

[Member C: summarize bootstrap.]

We use paired bootstrap resampling with 2,000 samples and seed 6120 to estimate uncertainty for pairwise system differences.

---

# 7 Results and Analysis

[Owner: Member C drafts; Member D integrates. Target: about 1.5 pages.]

## 7.1 Main Results

[Insert Table 2 here.]

Table 2: Main evaluation results on 200 test requests. Higher is better for CEFR exact accuracy and MeaningBERT scores. Lower is better for CEFR RMSE.

| System | CEFR Exact | CEFR RMSE | MB-source | MB-reference | Mean revisions |
|---|---:|---:|---:|---:|---:|
| Identity | 0.265 | 1.327 | 94.46 | 81.45 | 0.00 |
| Zero-shot | 0.165 | 1.526 | 82.75 | 76.28 | 0.00 |
| Three-shot | 0.200 | 1.444 | 84.93 | 76.48 | 0.00 |
| Self-refine | 0.175 | 1.515 | 82.84 | 76.40 | 1.04 |
| Human oracle | 0.625 | 0.612 | 80.84 | 94.41 | 0.00 |

[Replace table with generated version from main_results.csv in final paper.]

The three-shot system obtains the strongest generated-system CEFR exact accuracy and RMSE. Compared with zero-shot, three-shot improves exact accuracy from 0.165 to 0.200 and lowers RMSE from 1.526 to 1.444. It also improves MeaningBERT source similarity from 82.75 to 84.93.

Self-refinement performs close to zero-shot despite adding revisions. It reaches 0.175 exact accuracy and 1.515 RMSE, with an average of 1.04 revisions per request. The paired bootstrap intervals should be used to avoid overclaiming these small differences.

## 7.2 A2 versus B1

[Member C: insert compact A2/B1 analysis.]

Across systems, B1 is easier to control than A2. For example, three-shot reaches 0.320 exact accuracy on B1 but only 0.080 on A2. This suggests that the model often fails to simplify aggressively enough for A2.

Optional compact table:

| System | A2 Exact | B1 Exact | A2 RMSE | B1 RMSE |
|---|---:|---:|---:|---:|
| Zero-shot | 0.120 | 0.210 | 1.866 | 1.086 |
| Three-shot | 0.080 | 0.320 | 1.761 | 1.034 |
| Self-refine | 0.120 | 0.230 | 1.876 | 1.034 |

## 7.3 Qualitative Error Analysis

[Insert one short example. Keep compact.]

Source:

[Paste one source paragraph.]

Target level:

[A2 or B1.]

Zero-shot output:

[Paste output.]

Self-refined output:

[Paste output.]

Analysis:

[One or two sentences explaining whether the output is too complex, loses meaning, over-simplifies, hallucinates, or fails discourse/coreference.]

## 7.4 Discussion

The results suggest that examples are more useful than our lightweight feedback loop for this model. Three-shot prompting provides concrete demonstrations of the desired rewrite style, while self-refinement depends on a noisy level signal and asks the same small model to repair its own output. The gap between generated systems and the human-reference oracle shows that small open-weight models still struggle with precise CEFR control and meaning preservation on paragraph-level simplification.

---

# 8 Conclusion and Future Work

[Owner: Member D. Target: about 0.4 page.]

We evaluated zero-shot, three-shot, and CEFR-feedback self-refinement prompting for CEFR-controlled text simplification with a small open-weight instruction model. On the TSAR 2025 test requests, three-shot prompting produced the best generated-system results, while self-refinement added revision steps without clear aggregate improvement over zero-shot. The results also show a strong target-level asymmetry: B1 requests are easier than A2 requests across all generated systems.

Future work should test larger open-weight models, stronger example-selection strategies, reranking with separate readability and meaning models, and human evaluation of adequacy, fluency, and simplicity. A stronger refinement method may need more informative feedback than a predicted CEFR label alone.

---

# Limitations

[Owner: Member D. ACL requires this section after Conclusion and before References. Keep concise.]

This study has several limitations. First, we evaluate one small open-weight model, so the findings may not generalize to larger models or different model families. Second, the test set is small, with 200 target requests, limiting the strength of statistical conclusions. Third, the self-refinement loop depends on an automatic CEFR critic, and errors from this critic can affect revision behavior. Fourth, our evaluation relies on automatic CEFR and semantic similarity metrics; we do not report a full independent human evaluation. Finally, prompt wording and demonstration selection may influence the results, and we test only one fixed prompt configuration per condition.

---

# References

[Owner: Member D, with all members checking assigned citations.]

[Add references in ACL format, alphabetically by first author. Include DOI or ACL Anthology URL where possible.]

Example placeholders:

Alva-Manchego, Fernando, et al. 2020. ASSET: A Dataset for Tuning and Evaluation of Sentence Simplification Models with Multiple Rewriting Transformations. [Fill venue and URL.]

Maddela, Mounica, et al. 2023. LENS: A Learnable Evaluation Metric for Text Simplification. [Fill venue and URL.]

Xu, Wei, et al. 2016. Optimizing Statistical Machine Translation for Text Simplification. [Fill venue and URL.]

---

# Appendix A. Prompt Templates

[Optional. Not part of the main 8-page content if placed after references.]

[Paste direct, three-shot, and refinement prompt templates if needed.]

# Appendix B. Additional Results

[Optional.]

[Place full ALL/A2/B1 result table, extra qualitative examples, and extended bootstrap results here if they do not fit in the main paper.]

---

# Member Checklist

Member A:

- Replace Section 2.
- Replace Section 4.
- Add exact dataset statistics.
- Check dataset claims against `member_A_deliverables`.

Member B:

- Replace Section 5.
- Check model, decoding, prompt, and self-refinement details.
- Verify no claim says test references were used in prompts.

Member C:

- Replace Section 6.
- Replace Section 7 result text from `main_results.csv` and `pairwise_bootstrap.csv`.
- Add one qualitative example from `per_instance/*.jsonl`.

Member D:

- Write Abstract last.
- Finish Introduction, Related Work, Conclusion, Limitations.
- Ensure ACL formatting, citations, page limit, and tone are consistent.
- Check every major claim has evidence from a result table or citation.
