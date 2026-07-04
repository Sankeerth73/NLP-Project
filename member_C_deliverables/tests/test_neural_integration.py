import json
import os
from pathlib import Path

import pytest

from member_C_deliverables.scripts.scorers import (
    HuggingFaceCEFRScorer,
    HuggingFaceMeaningScorer,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_NEURAL_TESTS") != "1",
    reason="set RUN_NEURAL_TESTS=1 after downloading checkpoints",
)


def test_downloaded_checkpoints_smoke(tmp_path: Path) -> None:
    config = json.loads(
        Path("member_C_deliverables/configs/evaluation_v1.json").read_text()
    )
    cefr = HuggingFaceCEFRScorer(
        config["cefr_models"], cache_dir=tmp_path / "cefr", batch_size=1
    )
    meaning = HuggingFaceMeaningScorer(
        config["meaningbert"], cache_dir=tmp_path / "meaning", batch_size=1
    )

    prediction = cefr.score(["People use bridges to cross rivers."])[0]
    similarity = meaning.score_pairs(
        ["People use bridges to cross rivers."],
        ["People cross rivers using bridges."],
    )[0]

    assert prediction["label"] in {"A1", "A2", "B1", "B2", "C1", "C2"}
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert isinstance(similarity, float)
