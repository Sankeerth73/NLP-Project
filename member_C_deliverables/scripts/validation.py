from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class EvaluationDataError(ValueError):
    """Raised when evaluation inputs violate the handoff contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_expected_hashes(
    prediction_paths: list[Path], expected_hashes_path: Path
) -> dict[str, str]:
    payload = json.loads(expected_hashes_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("files"), dict):
        payload = payload["files"]
    if not isinstance(payload, dict):
        raise EvaluationDataError(
            f"{expected_hashes_path}: expected a JSON hash mapping"
        )
    verified: dict[str, str] = {}
    for path in prediction_paths:
        expected = payload.get(str(path), payload.get(path.name))
        if not isinstance(expected, str):
            raise EvaluationDataError(
                f"{expected_hashes_path}: no expected hash for {path}"
            )
        actual = sha256_file(path)
        if actual.lower() != expected.lower():
            raise EvaluationDataError(
                f"{path}: SHA-256 mismatch; expected {expected}, got {actual}"
            )
        verified[str(path)] = actual
    return verified


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvaluationDataError(
                    f"{path}:{line_number}: invalid JSON"
                ) from exc
            if not isinstance(row, dict):
                raise EvaluationDataError(
                    f"{path}:{line_number}: expected a JSON object"
                )
            rows.append(row)
    if not rows:
        raise EvaluationDataError(f"{path}: no records")
    return rows


def _index_unique(
    rows: list[dict[str, Any]], path: Path
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise EvaluationDataError(f"{path}: missing or empty id")
        if identifier in indexed:
            raise EvaluationDataError(f"{path}: duplicate id {identifier}")
        indexed[identifier] = row
    return indexed


def validate_and_align(
    dataset_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    *,
    dataset_path: Path,
    prediction_path: Path,
    split: str,
) -> list[dict[str, Any]]:
    """Validate one complete split and align predictions by ID."""
    expected_rows = [row for row in dataset_rows if row.get("split") == split]
    selected_predictions = [
        row for row in prediction_rows if row.get("split") == split
    ]
    if not expected_rows:
        raise EvaluationDataError(f"{dataset_path}: unknown split {split}")

    expected = _index_unique(expected_rows, dataset_path)
    predicted = _index_unique(selected_predictions, prediction_path)
    missing = sorted(set(expected) - set(predicted))
    extra = sorted(set(predicted) - set(expected))
    if missing:
        raise EvaluationDataError(
            f"{prediction_path}: missing ids {missing[:5]}"
        )
    if extra:
        raise EvaluationDataError(f"{prediction_path}: extra ids {extra[:5]}")

    aligned: list[dict[str, Any]] = []
    for identifier in sorted(expected):
        gold = expected[identifier]
        prediction = predicted[identifier]
        for field in ("source_id", "split", "target_level"):
            if prediction.get(field) != gold.get(field):
                raise EvaluationDataError(
                    f"{prediction_path}: {identifier} has mismatched {field}"
                )
        output = prediction.get("output")
        if not isinstance(output, str) or not output.strip():
            raise EvaluationDataError(
                f"{prediction_path}: {identifier} has empty output"
            )
        system = prediction.get("system")
        if not isinstance(system, str) or not system.strip():
            raise EvaluationDataError(
                f"{prediction_path}: {identifier} has empty system"
            )
        revision_count = prediction.get("revision_count")
        if not isinstance(revision_count, int) or revision_count < 0:
            raise EvaluationDataError(
                f"{prediction_path}: {identifier} has invalid revision_count"
            )
        aligned.append(
            {
                "id": identifier,
                "source_id": gold["source_id"],
                "split": split,
                "target_level": gold["target_level"],
                "source": gold["source"],
                "references": gold["references"],
                "system": system,
                "output": output.strip(),
                "revision_count": revision_count,
            }
        )
    systems = {row["system"] for row in aligned}
    if len(systems) != 1:
        raise EvaluationDataError(
            f"{prediction_path}: expected one system, found {sorted(systems)}"
        )
    return aligned
