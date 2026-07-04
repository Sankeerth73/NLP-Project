# Member C: Independent Evaluation Pipeline

This directory evaluates frozen prediction files without using Member B's
generation-time critic outputs. It validates and aligns records by `id`, runs the
three organizer-published CEFR checkpoints, reproduces the documented
confidence-based ensemble, scores source/output and reference/output pairs with
MeaningBERT, caches neural outputs, and writes per-instance and aggregate results.

## Current status

The complete harness and the identity-baseline evaluation are available. The
identity run covers all 200 test requests and is recorded in `results/`. Member B's
three systems cannot be scored until their frozen prediction files exist; no Member B
files were present when this baseline was run.

The identity rows copy the source exactly (`source_exact_rate = 1.0`). MeaningBERT
uses its native approximately 0–100 regression scale and gives identical paragraphs
about 94.5 rather than exactly 100, so textual identity and MeaningBERT similarity
are reported separately.

## Reproducibility

`configs/evaluation_v1.json` pins full Hugging Face commit hashes for all four
models. The CEFR label order is `A1, A2, B1, B2, C1, C2`. For each instance, the
ensemble selects the predicted label from whichever of the three classifiers has
the largest maximum softmax probability. This follows Section 3.2 of the TSAR 2025
shared-task paper.

Metric status:

- CEFR RMSE: official-method reproduction.
- MeaningBERT source and reference scores: official-model reproduction.
- Exact accuracy, adjacent accuracy, and weighted F1: supplementary.
- Adjacent accuracy counts predictions at most one ordinal CEFR level away.
- Paired bootstrap intervals use 2,000 resamples and seed 6120.

The organizers did not publish a standalone evaluation script. Therefore, this code
does not claim bit-for-bit identity with an unavailable official implementation.

## Commands

Install the neural dependency:

```bash
python3 -m pip install --user -r member_C_deliverables/requirements.txt
```

Run unit tests (neural calls are skipped):

```bash
python3 -m pytest member_C_deliverables/tests -q
```

Run the opt-in downloaded-checkpoint smoke test:

```bash
HF_HUB_DISABLE_XET=1 RUN_NEURAL_TESTS=1 \
python3 -m pytest member_C_deliverables/tests/test_neural_integration.py -q
```

Evaluate identity:

```bash
HF_HUB_DISABLE_XET=1 python3 -m member_C_deliverables.scripts.pipeline \
  --dataset member_A_deliverables/data/processed/tsar2025_normalized.jsonl \
  --predictions member_A_deliverables/data/processed/identity_baseline.jsonl \
  --output-dir member_C_deliverables/results \
  --config member_C_deliverables/configs/evaluation_v1.json \
  --split test \
  --backend neural
```

After Member B freezes predictions, pass all three files after `--predictions` in
one invocation. The evaluator checks each file's hash and exact split coverage,
rejects invalid records, and produces paired comparisons across systems.
Use `--expected-hashes member_B_deliverables/manifests/hashes.json` to compare
computed hashes with Member B's frozen hash mapping. Pass Member B's run and critic
manifests after `--upstream-manifests`; their hashes are then preserved in the
evaluation manifest without importing any critic predictions.

`--backend development` substitutes deterministic heuristic scorers for plumbing
checks only. Development scores must never be reported as experiment results.

## Outputs

- `results/per_instance/*.jsonl`: final independently recomputed scores.
- `results/aggregate/*.csv`: ALL/A2/B1 rows per system.
- `results/main_results.csv` and `.md`: paper-ready compact results.
- `results/pairwise_bootstrap.csv`: deterministic paired differences.
- `cache/`: content-addressed per-checkpoint probabilities and MeaningBERT scores.
- `manifests/`: data/prediction/config hashes, model revisions, and environment.

Primary method sources are the
[TSAR 2025 shared-task paper](https://aclanthology.org/2025.tsar-1.8/) and the
[MeaningBERT model card](https://huggingface.co/davebulaval/MeaningBERT).
