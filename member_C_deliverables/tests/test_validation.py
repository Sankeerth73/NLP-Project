import copy
import random
from pathlib import Path

import pytest

from member_C_deliverables.scripts.validation import (
    EvaluationDataError,
    validate_and_align,
)


def dataset_rows() -> list[dict[str, object]]:
    return [
        {
            "id": "01-a2",
            "source_id": "01",
            "split": "test",
            "target_level": "A2",
            "source": "A source.",
            "references": ["A reference."],
        },
        {
            "id": "01-b1",
            "source_id": "01",
            "split": "test",
            "target_level": "B1",
            "source": "A source.",
            "references": ["Another reference."],
        },
    ]


def prediction_rows() -> list[dict[str, object]]:
    return [
        {
            "id": "01-a2",
            "source_id": "01",
            "split": "test",
            "target_level": "A2",
            "system": "fixture",
            "output": "Simple text.",
            "revision_count": 0,
        },
        {
            "id": "01-b1",
            "source_id": "01",
            "split": "test",
            "target_level": "B1",
            "system": "fixture",
            "output": "Somewhat simple text.",
            "revision_count": 1,
        },
    ]


def align(predictions: list[dict[str, object]]) -> list[dict[str, object]]:
    return validate_and_align(
        dataset_rows(),
        predictions,
        dataset_path=Path("dataset.jsonl"),
        prediction_path=Path("predictions.jsonl"),
        split="test",
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda rows: rows.append(copy.deepcopy(rows[0])), "duplicate id"),
        (lambda rows: rows.pop(), "missing ids"),
        (
            lambda rows: rows.append(
                {
                    **copy.deepcopy(rows[0]),
                    "id": "99-a2",
                    "source_id": "99",
                }
            ),
            "extra ids",
        ),
        (
            lambda rows: rows[0].update(target_level="B1"),
            "mismatched target_level",
        ),
        (lambda rows: rows[0].update(output=""), "empty output"),
    ],
)
def test_invalid_predictions_rejected(mutation: object, message: str) -> None:
    rows = prediction_rows()
    mutation(rows)  # type: ignore[operator]
    with pytest.raises(EvaluationDataError, match=message):
        align(rows)


def test_join_is_invariant_to_prediction_order() -> None:
    ordered = prediction_rows()
    shuffled = copy.deepcopy(ordered)
    random.Random(42).shuffle(shuffled)

    assert align(ordered) == align(shuffled)


def test_rows_outside_requested_split_are_ignored() -> None:
    rows = prediction_rows()
    rows.append(
        {
            **copy.deepcopy(rows[0]),
            "id": "trial-a2",
            "source_id": "trial",
            "split": "trial",
        }
    )
    assert len(align(rows)) == 2
