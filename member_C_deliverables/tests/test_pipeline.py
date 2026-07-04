from typing import Any

from member_C_deliverables.scripts.pipeline import evaluate_predictions


class FixedCEFR:
    def score(self, texts: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "label": "A2",
                "confidence": 0.9,
                "selected_model": "independent-evaluator",
                "checkpoint_probabilities": {},
            }
            for _ in texts
        ]


class FixedMeaning:
    def score_pairs(self, first: list[str], second: list[str]) -> list[float]:
        return [0.75 for _ in first]


def test_generation_critic_metadata_cannot_affect_evaluation() -> None:
    row = {
        "id": "01-a2",
        "source_id": "01",
        "split": "test",
        "target_level": "A2",
        "source": "Source",
        "references": ["Reference"],
        "system": "fixture",
        "output": "Output",
        "revision_count": 1,
        "critic_prediction": "C2",
        "critic_confidence": 1.0,
    }
    result = evaluate_predictions([row], FixedCEFR(), FixedMeaning())[0]

    assert result["predicted_cefr"] == "A2"
    assert "critic_prediction" not in result
    assert result["source_exact_match"] is False
