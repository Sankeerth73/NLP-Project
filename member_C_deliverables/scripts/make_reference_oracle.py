from __future__ import annotations

import argparse
import json
from pathlib import Path

from member_C_deliverables.scripts.validation import load_jsonl


def make_reference_oracle(
    dataset_path: Path, output_path: Path, *, split: str
) -> None:
    rows = load_jsonl(dataset_path)
    predictions = []
    for row in rows:
        if row.get("split") != split:
            continue
        references = row.get("references")
        if not isinstance(references, list) or not references:
            raise ValueError(f"{row.get('id')} has no reference")
        predictions.append(
            {
                "id": row["id"],
                "source_id": row["source_id"],
                "split": row["split"],
                "target_level": row["target_level"],
                "system": "human_reference_oracle",
                "output": references[0],
                "seed": None,
                "revision_count": 0,
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in predictions
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a reference-oracle sanity prediction file"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=("trial", "test"), default="test")
    args = parser.parse_args()
    make_reference_oracle(args.dataset, args.output, split=args.split)


if __name__ == "__main__":
    main()
