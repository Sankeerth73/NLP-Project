import json
from pathlib import Path

from member_C_deliverables.scripts.make_reference_oracle import (
    make_reference_oracle,
)


def test_reference_oracle_uses_requested_split(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.jsonl"
    output = tmp_path / "oracle.jsonl"
    rows = [
        {
            "id": "01-a2",
            "source_id": "01",
            "split": "test",
            "target_level": "A2",
            "references": ["Easy text."],
        },
        {
            "id": "02-a2",
            "source_id": "02",
            "split": "trial",
            "target_level": "A2",
            "references": ["Trial text."],
        },
    ]
    dataset.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )

    make_reference_oracle(dataset, output, split="test")
    predictions = [json.loads(line) for line in output.read_text().splitlines()]

    assert len(predictions) == 1
    assert predictions[0]["output"] == "Easy text."
    assert predictions[0]["system"] == "human_reference_oracle"
