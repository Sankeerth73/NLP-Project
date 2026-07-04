from __future__ import annotations

import math
import random
from collections import Counter
from collections.abc import Callable, Iterable
from typing import Any

CEFR_ORDER = ("A1", "A2", "B1", "B2", "C1", "C2")
CEFR_ORDINAL = {label: index + 1 for index, label in enumerate(CEFR_ORDER)}


def ordinal_error(target: str, predicted: str) -> int:
    return CEFR_ORDINAL[predicted] - CEFR_ORDINAL[target]


def rmse(targets: Iterable[str], predictions: Iterable[str]) -> float:
    errors = [
        ordinal_error(target, predicted)
        for target, predicted in zip(targets, predictions, strict=True)
    ]
    if not errors:
        raise ValueError("RMSE requires at least one record")
    return math.sqrt(sum(error * error for error in errors) / len(errors))


def exact_accuracy(
    targets: Iterable[str], predictions: Iterable[str]
) -> float:
    pairs = list(zip(targets, predictions, strict=True))
    if not pairs:
        raise ValueError("accuracy requires at least one record")
    return sum(target == prediction for target, prediction in pairs) / len(pairs)


def adjacent_accuracy(
    targets: Iterable[str], predictions: Iterable[str]
) -> float:
    pairs = list(zip(targets, predictions, strict=True))
    if not pairs:
        raise ValueError("accuracy requires at least one record")
    return (
        sum(abs(ordinal_error(target, prediction)) <= 1 for target, prediction in pairs)
        / len(pairs)
    )


def weighted_f1(
    targets: Iterable[str], predictions: Iterable[str]
) -> float:
    target_list = list(targets)
    prediction_list = list(predictions)
    if len(target_list) != len(prediction_list):
        raise ValueError("target and prediction lengths differ")
    if not target_list:
        raise ValueError("F1 requires at least one record")
    support = Counter(target_list)
    weighted = 0.0
    for label, count in support.items():
        true_positive = sum(
            target == label and prediction == label
            for target, prediction in zip(
                target_list, prediction_list, strict=True
            )
        )
        false_positive = sum(
            target != label and prediction == label
            for target, prediction in zip(
                target_list, prediction_list, strict=True
            )
        )
        false_negative = count - true_positive
        denominator = 2 * true_positive + false_positive + false_negative
        label_f1 = 0.0 if denominator == 0 else 2 * true_positive / denominator
        weighted += count * label_f1
    return weighted / len(target_list)


def aggregate_rows(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for target_group in ("ALL", "A2", "B1"):
        selected = (
            rows
            if target_group == "ALL"
            else [row for row in rows if row["target_level"] == target_group]
        )
        if not selected:
            continue
        targets = [row["target_level"] for row in selected]
        predictions = [row["predicted_cefr"] for row in selected]
        aggregates.append(
            {
                "system": selected[0]["system"],
                "target": target_group,
                "n": len(selected),
                "cefr_exact_accuracy": exact_accuracy(targets, predictions),
                "cefr_adjacent_accuracy": adjacent_accuracy(
                    targets, predictions
                ),
                "cefr_rmse": rmse(targets, predictions),
                "cefr_weighted_f1": weighted_f1(targets, predictions),
                "meaningbert_source": _mean(
                    row["meaningbert_source"] for row in selected
                ),
                "meaningbert_reference": _mean(
                    row["meaningbert_reference"] for row in selected
                ),
                "source_exact_rate": _mean(
                    float(row.get("source_exact_match", False))
                    for row in selected
                ),
                "mean_revisions": _mean(
                    row["revision_count"] for row in selected
                ),
            }
        )
    return aggregates


def paired_bootstrap_difference(
    first: list[float],
    second: list[float],
    *,
    seed: int,
    samples: int = 2000,
    confidence: float = 0.95,
    statistic: Callable[[list[float]], float] | None = None,
) -> dict[str, float]:
    if len(first) != len(second) or not first:
        raise ValueError("paired inputs must have the same non-zero length")
    if samples < 1:
        raise ValueError("samples must be positive")
    stat = statistic or _mean
    differences = [a - b for a, b in zip(first, second, strict=True)]
    rng = random.Random(seed)
    estimates = sorted(
        stat([differences[rng.randrange(len(differences))] for _ in differences])
        for _ in range(samples)
    )
    tail = (1.0 - confidence) / 2.0
    low_index = max(0, math.floor(tail * samples))
    high_index = min(samples - 1, math.ceil((1.0 - tail) * samples) - 1)
    return {
        "difference": stat(differences),
        "ci_low": estimates[low_index],
        "ci_high": estimates[high_index],
    }


def _mean(values: Iterable[float | int]) -> float:
    collected = list(values)
    if not collected:
        raise ValueError("mean requires at least one value")
    return sum(collected) / len(collected)
