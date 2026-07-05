# Member C → Member D Handoff: Evaluation Results and Paper Integration

## Purpose

This document transfers Member C's reproducible evaluation artifacts to Member D.
Use the structured result files as the only source of metric values. Do not manually
copy values from this document if the CSV files have since been regenerated.

## Delivery Status

As of 2026-07-04, the evaluation harness is complete, locally verified, and the
**final full-system evaluation has been run**. It has evaluated, in a single
consistent neural run:

- the identity baseline (all 200 test requests);
- the human-reference oracle (all 200 test requests);
- Member B's `open_model_zero_shot`, `open_model_three_shot`, and
  `open_model_self_refine` systems (all 200 test requests each).

Member B's three frozen prediction files were received, and each file's SHA-256 was
verified against Member B's own manifests (`da130e0…`, `e774435…`, `2d5c9c5…`) before
scoring. All final CEFR and MeaningBERT scores were **independently recomputed from
the output text**; Member B's generation-time critic scores were not used, and no
critic fields are present in the prediction files. RQ1–RQ3 can now be addressed from
the table below and `main_results.csv`.

## Files for Member D

Use:

- `member_C_deliverables/results/main_results.csv` — paper table source;
- `member_C_deliverables/results/main_results.md` — human-readable table;
- `member_C_deliverables/results/per_instance/*.jsonl` — error analysis and sampling;
- `member_C_deliverables/results/aggregate/*.csv` — per-system ALL/A2/B1 results;
- `member_C_deliverables/results/pairwise_bootstrap.csv` — paired uncertainty;
- `member_C_deliverables/results/sanity_checks.md` — five manually checked joins;
- `member_C_deliverables/manifests/evaluation_neural_test.json` — exact hashes,
  model revisions, environment, and settings;
- `member_C_deliverables/configs/evaluation_v1.json` — evaluator configuration;
- `member_C_deliverables/README.md` — reproduction commands and metric caveats.

Do not use `results/development_smoke/` for the paper. It contains deliberately
non-neural plumbing scores.

## Final Results

Values below are copied from `main_results.csv` for convenience only; regenerate the
paper table from the CSV. Mean revisions are 0 for all systems except
`open_model_self_refine`.

| System | Target | N | CEFR exact ↑ | CEFR RMSE ↓ | MB-source ↑ | MB-reference ↑ | Mean rev. |
|---|---|---:|---:|---:|---:|---:|---:|
| Identity | ALL | 200 | 0.2650 | 1.3266 | 94.4612 | 81.4519 | 0.00 |
| Identity | A2 | 100 | 0.0800 | 1.6523 | 94.4612 | 78.0577 | 0.00 |
| Identity | B1 | 100 | 0.4500 | 0.8888 | 94.4612 | 84.8461 | 0.00 |
| Human-reference oracle | ALL | 200 | 0.6250 | 0.6124 | 80.8381 | 94.4064 | 0.00 |
| Human-reference oracle | A2 | 100 | 0.6400 | 0.6000 | 77.1183 | 94.5118 | 0.00 |
| Human-reference oracle | B1 | 100 | 0.6100 | 0.6245 | 84.5580 | 94.3011 | 0.00 |
| open_model_zero_shot | ALL | 200 | 0.1650 | 1.5264 | 82.7452 | 76.2837 | 0.00 |
| open_model_zero_shot | A2 | 100 | 0.1200 | 1.8655 | 83.0823 | 72.4056 | 0.00 |
| open_model_zero_shot | B1 | 100 | 0.2100 | 1.0863 | 82.4082 | 80.1618 | 0.00 |
| open_model_three_shot | ALL | 200 | 0.2000 | 1.4440 | 84.9343 | 76.4815 | 0.00 |
| open_model_three_shot | A2 | 100 | 0.0800 | 1.7607 | 84.0336 | 73.1320 | 0.00 |
| open_model_three_shot | B1 | 100 | 0.3200 | 1.0344 | 85.8349 | 79.8309 | 0.00 |
| open_model_self_refine | ALL | 200 | 0.1750 | 1.5149 | 82.8383 | 76.3992 | 1.04 |
| open_model_self_refine | A2 | 100 | 0.1200 | 1.8762 | 82.7080 | 72.4996 | 0.65 |
| open_model_self_refine | B1 | 100 | 0.2300 | 1.0344 | 82.9687 | 80.2987 | 1.42 |

Interpretation supported by these numbers (confirm significance against
`pairwise_bootstrap.csv` before making claims):

- **Sanity baselines behave as expected.** Identity preserves the source exactly
  (`source_exact_rate = 1.0`) but controls target level poorly, especially for A2. The
  human-reference oracle inverts this: best CEFR control and highest reference
  similarity, lower source overlap — the expected simplification-versus-source
  trade-off.
- **RQ1 (prompting):** three-shot beats zero-shot on CEFR exact accuracy
  (0.200 vs 0.165 ALL) and on MB-source (84.93 vs 82.75), i.e. few-shot demonstrations
  improved both target control and source-meaning preservation for this 0.5B model.
- **RQ2 (self-refinement):** self-refine performed on average ~1.04 revisions (more on
  B1: 1.42) but its aggregate metrics are essentially indistinguishable from zero-shot
  (exact 0.175 vs 0.165; MB-source 82.84 vs 82.75). Any improvement claim must be
  checked against the paired bootstrap intervals; on these aggregates the effect looks
  negligible.
- **Difficulty asymmetry:** every system controls B1 far better than A2 (much lower
  RMSE, higher exact accuracy for B1). A2 is the harder target across the board.
- All generated systems sit well below the oracle on CEFR control, and below identity
  on source overlap — consistent with a small model that both under-controls level and
  drifts from the source.

## Metric Definitions and Reporting Labels

CEFR predictions use the three organizer-published ModernBERT checkpoints. For each
instance, the evaluator selects the prediction from the checkpoint with the highest
maximum softmax confidence. The ordinal mapping is:

`A1=1, A2=2, B1=3, B2=4, C1=5, C2=6`.

- CEFR RMSE: lower is better; label as an official-method reproduction.
- CEFR exact accuracy: higher is better; supplementary.
- Adjacent accuracy: higher is better; predictions within one ordinal step count as
  correct; supplementary.
- Weighted F1: higher is better; supplementary.
- MeaningBERT source/reference: higher is better; native approximately 0–100 scale;
  label as an official-model reproduction.

Important caveat: MeaningBERT gives identical paragraphs about 94.5 rather than
exactly 100. State that identity is textually exact and report the learned metric
separately. Do not rescale MeaningBERT values or describe them as percentages unless
the paper explicitly defines that presentation.

The organizers' shared-task paper specifies the metrics and confidence ensemble but
does not publish a standalone evaluator script. Therefore, use “reproduction,” not
“official implementation,” for Member C's code.

## Reproducibility Record

Pinned model commits:

- `AbdullahBarayan/ModernBERT-base-doc_sent_en-Cefr`:
  `b00d1d4780e46f6410ea8a8509649044dee18298`
- `AbdullahBarayan/ModernBERT-base-doc_en-Cefr`:
  `3c29f5fbcdc753e99bb437ff9303df983486915b`
- `AbdullahBarayan/ModernBERT-base-reference_AllLang2-Cefr2`:
  `83337437aa82277e96b293665dc3186088a4a839`
- `davebulaval/MeaningBERT`:
  `f40ff1edfdf9f6a6121eb5701b8557426a268495`

Environment used for the delivered (final) results:

- Python 3.10.9
- PyTorch 2.12.0
- Transformers 4.53.1
- macOS 26.5.1 arm64, device selected automatically (`auto` → CUDA/MPS/CPU)
- bootstrap seed 6120, 2,000 paired resamples

The exact recorded values are in `manifests/evaluation_neural_test.json`. This run
supersedes the earlier identity/oracle-only baseline; identity and oracle scores match
that baseline to ~6 decimal places (neural float nondeterminism), and CEFR labels and
RMSE are unchanged.

The exact dataset, prediction, config, and expected-hash-file SHA-256 values are in
`member_C_deliverables/manifests/evaluation_neural_test.json`.

## Finalization (completed)

The final evaluator run has been executed and is the source of the table above. The
exact command used:

```bash
TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_XET=1 HF_HUB_OFFLINE=1 \
python3 -m member_C_deliverables.scripts.pipeline \
  --dataset member_A_deliverables/data/processed/tsar2025_normalized.jsonl \
  --predictions \
    member_A_deliverables/data/processed/identity_baseline.jsonl \
    member_C_deliverables/results/sanity/reference_oracle_predictions.jsonl \
    member_B_deliverables/predictions/zero_shot.jsonl \
    member_B_deliverables/predictions/three_shot.jsonl \
    member_B_deliverables/predictions/self_refine.jsonl \
  --output-dir member_C_deliverables/results \
  --config member_C_deliverables/configs/evaluation_v1.json \
  --split test --backend neural \
  --expected-hashes member_C_deliverables/manifests/expected_hashes_all.json \
  --upstream-manifests \
    member_B_deliverables/manifests/zero_shot.json \
    member_B_deliverables/manifests/three_shot.json \
    member_B_deliverables/manifests/self_refine.json
```

Notes on how this differed from the originally-planned command shape:

1. A combined hash file, `member_C_deliverables/manifests/expected_hashes_all.json`,
   was used instead of Member B's `hashes.json` alone, because the single run also
   scores identity and the oracle, and `--expected-hashes` requires an entry for every
   prediction file passed. Member B's three hashes inside it are identical to Member
   B's own manifests; a Member-B-only file (`member_B_deliverables/manifests/hashes.json`)
   is also present and verifies the same three hashes.
2. Member B did **not** deliver a `critic/manifest.json`; the message stated the
   critic was `AbdullahBarayan/ModernBERT-base-doc_en-Cefr`, generation-time only. The
   directory `member_B_deliverables/critic/` exists but is empty. No critic scores were
   imported. If Member B later supplies the critic manifest, add it to
   `--upstream-manifests` and rerun to preserve its hash in the evaluation manifest.
3. All three Member B files validated: exactly 200 test IDs each, one prediction per
   ID, no empty outputs, no split/target mismatch, and no critic fields present.

Do not bypass a hash mismatch on any rerun.

## Paper Integration Rules

- Generate the LaTeX table from `main_results.csv`; do not hand-enter scores.
- Use `per_instance/*.jsonl` for reproducible qualitative sampling.
- Treat positive paired-bootstrap differences according to the
  `positive_favors` column.
- Keep Member B's generation-time critic separate from Member C's independent final
  evaluator.
- Do not call the reference oracle a deployable system.
- No human ratings were produced by Member C. Do not describe automatic scores as
  human evaluation.
- Do not claim statistical significance merely because a confidence interval is
  present; state the interval and whether it excludes zero.
- Preserve the release discrepancy: the evaluated pinned release contains 100 test
  sources and 200 target requests, even though the shared-task paper describes 80
  test sources.

## Current Blocker for Member D

The Results section comparing prompting conditions is blocked only on Member B's
frozen prediction bundle and hashes. Member D can already integrate the evaluation
method, reproducibility details, identity/oracle sanity discussion, and table
generation code.
