from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

from member_C_deliverables.scripts.metrics import (
    aggregate_rows,
    ordinal_error,
    paired_bootstrap_difference,
)
from member_C_deliverables.scripts.scorers import (
    CEFRScorer,
    HeuristicCEFRScorer,
    HuggingFaceCEFRScorer,
    HuggingFaceMeaningScorer,
    MeaningScorer,
    TokenOverlapMeaningScorer,
)
from member_C_deliverables.scripts.validation import (
    load_jsonl,
    sha256_file,
    validate_and_align,
    verify_expected_hashes,
)


def evaluate_predictions(
    aligned: list[dict[str, Any]],
    cefr_scorer: CEFRScorer,
    meaning_scorer: MeaningScorer,
) -> list[dict[str, Any]]:
    outputs = [row["output"] for row in aligned]
    cefr_scores = cefr_scorer.score(outputs)
    source_scores = meaning_scorer.score_pairs(
        [row["source"] for row in aligned], outputs
    )
    flat_references: list[str] = []
    flat_outputs: list[str] = []
    reference_counts: list[int] = []
    for row in aligned:
        references = row["references"]
        if not references:
            raise ValueError(f"{row['id']} has no references")
        reference_counts.append(len(references))
        flat_references.extend(references)
        flat_outputs.extend([row["output"]] * len(references))
    flat_reference_scores = meaning_scorer.score_pairs(
        flat_references, flat_outputs
    )
    reference_scores: list[float] = []
    offset = 0
    for count in reference_counts:
        scores = flat_reference_scores[offset : offset + count]
        reference_scores.append(sum(scores) / count)
        offset += count

    evaluated: list[dict[str, Any]] = []
    for row, cefr, source_score, reference_score in zip(
        aligned,
        cefr_scores,
        source_scores,
        reference_scores,
        strict=True,
    ):
        error = ordinal_error(row["target_level"], cefr["label"])
        evaluated.append(
            {
                "id": row["id"],
                "source_id": row["source_id"],
                "split": row["split"],
                "system": row["system"],
                "target_level": row["target_level"],
                "predicted_cefr": cefr["label"],
                "cefr_confidence": cefr["confidence"],
                "cefr_selected_model": cefr["selected_model"],
                "cefr_checkpoint_probabilities": cefr[
                    "checkpoint_probabilities"
                ],
                "exact_match": error == 0,
                "ordinal_error": error,
                "meaningbert_source": source_score,
                "meaningbert_reference": reference_score,
                "source_exact_match": row["source"] == row["output"],
                "revision_count": row["revision_count"],
            }
        )
    return evaluated


def run_evaluation(
    *,
    dataset_path: Path,
    prediction_paths: list[Path],
    output_dir: Path,
    config_path: Path,
    split: str = "test",
    backend: str = "neural",
    expected_hashes_path: Path | None = None,
    upstream_manifest_paths: list[Path] | None = None,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    per_instance_dir = output_dir / "per_instance"
    aggregate_dir = output_dir / "aggregate"
    deliverable_dir = config_path.parent.parent
    cache_dir = deliverable_dir / "cache"
    manifests_dir = deliverable_dir / "manifests"
    for directory in (per_instance_dir, aggregate_dir, cache_dir, manifests_dir):
        directory.mkdir(parents=True, exist_ok=True)

    if backend == "neural":
        cefr_scorer: CEFRScorer = HuggingFaceCEFRScorer(
            config["cefr_models"],
            cache_dir=cache_dir / "cefr",
            batch_size=config["inference"]["batch_size"],
            device=config["inference"]["device"],
        )
        meaning_scorer: MeaningScorer = HuggingFaceMeaningScorer(
            config["meaningbert"],
            cache_dir=cache_dir / "meaningbert",
            batch_size=config["inference"]["batch_size"],
            device=config["inference"]["device"],
        )
    elif backend == "development":
        cefr_scorer = HeuristicCEFRScorer()
        meaning_scorer = TokenOverlapMeaningScorer()
    else:
        raise ValueError(f"unknown backend: {backend}")

    dataset_rows = load_jsonl(dataset_path)
    if expected_hashes_path is not None:
        prediction_hashes = verify_expected_hashes(
            prediction_paths, expected_hashes_path
        )
    else:
        prediction_hashes = {}
    all_evaluated: list[dict[str, Any]] = []
    all_aggregates: list[dict[str, Any]] = []
    seen_systems: set[str] = set()
    for prediction_path in prediction_paths:
        predictions = load_jsonl(prediction_path)
        aligned = validate_and_align(
            dataset_rows,
            predictions,
            dataset_path=dataset_path,
            prediction_path=prediction_path,
            split=split,
        )
        evaluated = evaluate_predictions(aligned, cefr_scorer, meaning_scorer)
        system = evaluated[0]["system"]
        if system in seen_systems:
            raise ValueError(f"duplicate system across prediction files: {system}")
        seen_systems.add(system)
        system_filename = _safe_filename(system)
        _write_jsonl(per_instance_dir / f"{system_filename}.jsonl", evaluated)
        aggregates = aggregate_rows(evaluated)
        _write_csv(aggregate_dir / f"{system_filename}.csv", aggregates)
        all_evaluated.extend(evaluated)
        all_aggregates.extend(aggregates)
        prediction_hashes[str(prediction_path)] = sha256_file(prediction_path)

    _write_csv(output_dir / "main_results.csv", all_aggregates)
    _write_markdown(output_dir / "main_results.md", all_aggregates, backend)
    comparisons = _pairwise_comparisons(
        all_evaluated,
        seed=config["bootstrap"]["seed"],
        samples=config["bootstrap"]["samples"],
    )
    _write_csv(output_dir / "pairwise_bootstrap.csv", comparisons)
    manifest = {
        "schema_version": 1,
        "backend": backend,
        "split": split,
        "dataset": {
            "path": str(dataset_path),
            "sha256": sha256_file(dataset_path),
        },
        "predictions": prediction_hashes,
        "expected_hashes": (
            {
                "path": str(expected_hashes_path),
                "sha256": sha256_file(expected_hashes_path),
                "verified": True,
            }
            if expected_hashes_path is not None
            else None
        ),
        "upstream_manifests": {
            str(path): sha256_file(path)
            for path in (upstream_manifest_paths or [])
        },
        "config": {
            "path": str(config_path),
            "sha256": sha256_file(config_path),
        },
        "models": {
            "cefr": config["cefr_models"],
            "cefr_ensemble": config["cefr_ensemble"],
            "meaningbert": config["meaningbert"],
        },
        "bootstrap": config["bootstrap"],
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": _package_version("torch"),
            "transformers": _package_version("transformers"),
        },
    }
    manifest_path = manifests_dir / f"evaluation_{backend}_{split}.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _safe_filename(system: str) -> str:
    filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", system).strip("._")
    if not filename:
        raise ValueError(f"system name cannot form a safe filename: {system!r}")
    return filename


def _pairwise_comparisons(
    rows: list[dict[str, Any]], *, seed: int, samples: int
) -> list[dict[str, Any]]:
    systems = sorted({row["system"] for row in rows})
    by_system = {
        system: {row["id"]: row for row in rows if row["system"] == system}
        for system in systems
    }
    comparisons: list[dict[str, Any]] = []
    metrics = (
        ("exact_match", 1.0),
        ("meaningbert_source", 1.0),
        ("meaningbert_reference", 1.0),
        ("squared_ordinal_error", -1.0),
    )
    for left_index, left in enumerate(systems):
        for right in systems[left_index + 1 :]:
            common_ids = sorted(set(by_system[left]) & set(by_system[right]))
            for metric, direction in metrics:
                left_values = [
                    _metric_value(by_system[left][identifier], metric) * direction
                    for identifier in common_ids
                ]
                right_values = [
                    _metric_value(by_system[right][identifier], metric) * direction
                    for identifier in common_ids
                ]
                result = paired_bootstrap_difference(
                    left_values,
                    right_values,
                    seed=seed,
                    samples=samples,
                )
                comparisons.append(
                    {
                        "system_a": left,
                        "system_b": right,
                        "metric": metric,
                        "positive_favors": left,
                        "n": len(common_ids),
                        **result,
                        "seed": seed,
                        "samples": samples,
                    }
                )
    return comparisons


def _metric_value(row: dict[str, Any], metric: str) -> float:
    if metric == "squared_ordinal_error":
        return float(row["ordinal_error"] ** 2)
    return float(row[metric])


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(
    path: Path, rows: list[dict[str, Any]], backend: str
) -> None:
    columns = (
        ("System", "system"),
        ("Target", "target"),
        ("N", "n"),
        ("CEFR exact acc.", "cefr_exact_accuracy"),
        ("CEFR RMSE", "cefr_rmse"),
        ("MB-source", "meaningbert_source"),
        ("MB-reference", "meaningbert_reference"),
        ("Mean revisions", "mean_revisions"),
    )
    lines = [
        "# Main Results",
        "",
        f"Backend: `{backend}`.",
        "",
        "| " + " | ".join(header for header, _ in columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for row in rows:
        values = []
        for _, key in columns:
            value = row[key]
            values.append(f"{value:.4f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen predictions")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument(
        "--predictions", type=Path, nargs="+", required=True
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--split", default="test", choices=("trial", "test"))
    parser.add_argument(
        "--backend", default="neural", choices=("neural", "development")
    )
    parser.add_argument("--expected-hashes", type=Path)
    parser.add_argument("--upstream-manifests", type=Path, nargs="*", default=[])
    args = parser.parse_args()
    run_evaluation(
        dataset_path=args.dataset,
        prediction_paths=args.predictions,
        output_dir=args.output_dir,
        config_path=args.config,
        split=args.split,
        backend=args.backend,
        expected_hashes_path=args.expected_hashes,
        upstream_manifest_paths=args.upstream_manifests,
    )


if __name__ == "__main__":
    main()
