import hashlib
import json
from pathlib import Path

import pytest

from member_C_deliverables.scripts.validation import (
    EvaluationDataError,
    verify_expected_hashes,
)


def test_expected_prediction_hashes_are_verified(tmp_path: Path) -> None:
    prediction = tmp_path / "predictions.jsonl"
    prediction.write_text('{"id": "1"}\n', encoding="utf-8")
    digest = hashlib.sha256(prediction.read_bytes()).hexdigest()
    hashes = tmp_path / "hashes.json"
    hashes.write_text(json.dumps({prediction.name: digest}), encoding="utf-8")

    assert verify_expected_hashes([prediction], hashes) == {
        str(prediction): digest
    }

    hashes.write_text(json.dumps({prediction.name: "0" * 64}), encoding="utf-8")
    with pytest.raises(EvaluationDataError, match="SHA-256 mismatch"):
        verify_expected_hashes([prediction], hashes)
