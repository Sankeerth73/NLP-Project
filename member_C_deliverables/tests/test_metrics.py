import pytest

from member_C_deliverables.scripts.metrics import (
    adjacent_accuracy,
    aggregate_rows,
    exact_accuracy,
    paired_bootstrap_difference,
    rmse,
)


def evaluated_rows() -> list[dict[str, object]]:
    return [
        {
            "system": "fixture",
            "target_level": "A2",
            "predicted_cefr": "A2",
            "meaningbert_source": 0.8,
            "meaningbert_reference": 0.7,
            "source_exact_match": True,
            "revision_count": 0,
        },
        {
            "system": "fixture",
            "target_level": "B1",
            "predicted_cefr": "B2",
            "meaningbert_source": 0.6,
            "meaningbert_reference": 0.9,
            "source_exact_match": False,
            "revision_count": 2,
        },
    ]


def test_cefr_metrics_match_hand_calculation() -> None:
    targets = ["A2", "B1", "C1"]
    predictions = ["A2", "B2", "B1"]

    assert exact_accuracy(targets, predictions) == pytest.approx(1 / 3)
    assert adjacent_accuracy(targets, predictions) == pytest.approx(2 / 3)
    assert rmse(targets, predictions) == pytest.approx((5 / 3) ** 0.5)


def test_aggregation_separates_targets() -> None:
    rows = aggregate_rows(evaluated_rows())
    by_target = {row["target"]: row for row in rows}

    assert set(by_target) == {"ALL", "A2", "B1"}
    assert by_target["ALL"]["n"] == 2
    assert by_target["A2"]["cefr_exact_accuracy"] == 1.0
    assert by_target["B1"]["cefr_rmse"] == 1.0
    assert by_target["ALL"]["mean_revisions"] == 1.0
    assert by_target["ALL"]["source_exact_rate"] == 0.5


def test_bootstrap_is_deterministic() -> None:
    kwargs = {"seed": 42, "samples": 200}
    first = paired_bootstrap_difference([1, 2, 3], [0, 1, 1], **kwargs)
    second = paired_bootstrap_difference([1, 2, 3], [0, 1, 1], **kwargs)

    assert first == second
