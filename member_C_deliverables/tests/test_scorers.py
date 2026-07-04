from pathlib import Path
from typing import Any

from member_C_deliverables.scripts.scorers import (
    HuggingFaceCEFRScorer,
    HuggingFaceMeaningScorer,
)


MODELS = [
    {"id": f"fixture/model-{index}", "revision": "abc"}
    for index in range(3)
]


class StubCEFRScorer(HuggingFaceCEFRScorer):
    calls = 0

    def _run_checkpoint(
        self, config: dict[str, str], texts: list[str]
    ) -> list[dict[str, Any]]:
        self.calls += 1
        index = int(config["id"][-1])
        confidence = (0.6, 0.9, 0.7)[index]
        label = ("A2", "B1", "B2")[index]
        return [
            {
                "label": label,
                "confidence": confidence,
                "probabilities": {label: confidence},
            }
            for _ in texts
        ]


class StubMeaningScorer(HuggingFaceMeaningScorer):
    calls = 0

    def _run_pairs(self, first: list[str], second: list[str]) -> list[float]:
        self.calls += 1
        return [1.0 if left == right else 0.25 for left, right in zip(first, second)]


def test_confidence_ensemble_and_cache_are_deterministic(tmp_path: Path) -> None:
    first = StubCEFRScorer(MODELS, cache_dir=tmp_path)
    scores = first.score(["Some text."])
    assert scores[0]["label"] == "B1"
    assert scores[0]["selected_model"] == "fixture/model-1"
    assert first.calls == 3

    second = StubCEFRScorer(MODELS, cache_dir=tmp_path)
    assert second.score(["Some text."]) == scores
    assert second.calls == 0


def test_meaning_scorer_cached_and_uncached_match(tmp_path: Path) -> None:
    config = {"id": "fixture/meaning", "revision": "abc"}
    first = StubMeaningScorer(config, cache_dir=tmp_path)
    scores = first.score_pairs(["same", "left"], ["same", "right"])
    assert scores == [1.0, 0.25]
    assert first.calls == 1

    second = StubMeaningScorer(config, cache_dir=tmp_path)
    assert second.score_pairs(["same", "left"], ["same", "right"]) == scores
    assert second.calls == 0
