# Member C → Member D Handoff: Evaluation Results and Paper Integration

## Purpose

This document transfers Member C's reproducible evaluation artifacts to Member D.
Use the structured result files as the only source of metric values. Do not manually
copy values from this document if the CSV files have since been regenerated.

## Delivery Status

As of 2026-07-04, the evaluation harness is complete and locally verified. It has
evaluated:

- the identity baseline on all 200 test requests;
- the human-reference oracle on all 200 test requests.

Member B's zero-shot, three-shot, and self-refinement prediction files do not yet
exist in this workspace. Consequently, the current table is a verified baseline and
sanity table, not the final experimental comparison. Do not answer RQ1–RQ3 or claim a
prompting/self-refinement improvement until Member B's frozen files are evaluated.

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

## Current Verified Results

| System | Target | N | CEFR exact ↑ | CEFR RMSE ↓ | MB-source ↑ | MB-reference ↑ |
|---|---|---:|---:|---:|---:|---:|
| Identity | ALL | 200 | 0.2650 | 1.3266 | 94.4612 | 81.4519 |
| Identity | A2 | 100 | 0.0800 | 1.6523 | 94.4612 | 78.0577 |
| Identity | B1 | 100 | 0.4500 | 0.8888 | 94.4612 | 84.8461 |
| Human-reference oracle | ALL | 200 | 0.6250 | 0.6124 | 80.8381 | 94.4064 |
| Human-reference oracle | A2 | 100 | 0.6400 | 0.6000 | 77.1183 | 94.5118 |
| Human-reference oracle | B1 | 100 | 0.6100 | 0.6245 | 84.5580 | 94.3011 |

Interpretation that is supported now:

- Identity preserves the source text exactly (`source_exact_rate = 1.0`) but has poor
  target-level control, especially for A2.
- The human-reference oracle has lower CEFR RMSE and higher reference similarity than
  identity, while its source similarity is lower. This is the expected
  simplification-versus-source-overlap direction.
- These are sanity baselines. They do not establish how any generated system behaves.

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

Environment used for the delivered results:

- Python 3.12.8
- PyTorch 2.12.0
- Transformers 4.53.1
- macOS 15.5 arm64, MPS selected automatically
- bootstrap seed 6120, 2,000 paired resamples

The exact dataset, prediction, config, and expected-hash-file SHA-256 values are in
`member_C_deliverables/manifests/evaluation_neural_test.json`.

## Finalization After Member B Delivers

Before Member D writes the final Results section, Member C must rerun the evaluator
with identity plus all three frozen Member B systems. The run must:

1. receive Member B's expected SHA-256 mapping through `--expected-hashes`;
2. receive Member B's generation and critic manifests through
   `--upstream-manifests`;
3. validate exactly 200 test IDs per system;
4. overwrite `results/main_results.csv`, `.md`, per-instance files, bootstrap file,
   and the neural evaluation manifest;
5. retain ALL, A2, and B1 rows for every system.

Expected command shape:

```bash
HF_HUB_OFFLINE=1 python3 -m member_C_deliverables.scripts.pipeline \
  --dataset member_A_deliverables/data/processed/tsar2025_normalized.jsonl \
  --predictions \
    member_A_deliverables/data/processed/identity_baseline.jsonl \
    member_B_deliverables/predictions/zero_shot.jsonl \
    member_B_deliverables/predictions/three_shot.jsonl \
    member_B_deliverables/predictions/self_refine.jsonl \
  --output-dir member_C_deliverables/results \
  --config member_C_deliverables/configs/evaluation_v1.json \
  --split test \
  --backend neural \
  --expected-hashes member_B_deliverables/manifests/hashes.json \
  --upstream-manifests \
    member_B_deliverables/manifests/zero_shot.json \
    member_B_deliverables/manifests/three_shot.json \
    member_B_deliverables/manifests/self_refine.json \
    member_B_deliverables/critic/manifest.json
```

Adjust only the hash-file path if Member B uses a different filename. Do not bypass a
hash mismatch.

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
