from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRIVATE_KEY = ROOT / "human_eval_key_private.csv"
SYSTEMS = ["zero_shot", "three_shot", "self_refine"]
RATING_FIELDS = ["meaning", "fluency", "cefr_fit"]


def parse_score(value: str, *, row_num: int, field: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        score = float(value)
    except ValueError as exc:
        raise ValueError(f"Row {row_num}: {field} must be a number from 1 to 5") from exc
    if score < 1 or score > 5:
        raise ValueError(f"Row {row_num}: {field}={score} is outside 1 to 5")
    return score


def read_key() -> dict[tuple[str, str], str]:
    mapping = {}
    with PRIVATE_KEY.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            example_id = row["example_id"]
            for label in ("A", "B", "C"):
                mapping[(example_id, label)] = row[f"output_{label}_system"]
    return mapping


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize filled human evaluation ratings exported from Google Sheets."
    )
    parser.add_argument("ratings_csv", help="Filled CSV exported from Google Sheets")
    parser.add_argument(
        "--output",
        default=str(ROOT / "human_eval_summary_by_system.csv"),
        help="Output summary CSV path",
    )
    args = parser.parse_args()

    key = read_key()
    scores: dict[str, dict[str, list[float]]] = {
        system: {field: [] for field in RATING_FIELDS} for system in SYSTEMS
    }
    win_counts: Counter[str] = Counter()
    tie_count = 0
    completed_rows = 0
    annotators = set()
    examples = set()

    with Path(args.ratings_csv).open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            example_id = row["example_id"].strip()
            if not example_id:
                continue
            annotator_id = row.get("annotator_id", "").strip()
            if annotator_id:
                annotators.add(annotator_id)
            examples.add(example_id)

            row_has_score = False
            for label in ("A", "B", "C"):
                system = key[(example_id, label)]
                field_map = {
                    "meaning": f"{label}_meaning_1_5",
                    "fluency": f"{label}_fluency_1_5",
                    "cefr_fit": f"{label}_cefr_fit_1_5",
                }
                for metric, column in field_map.items():
                    score = parse_score(row.get(column, ""), row_num=row_num, field=column)
                    if score is not None:
                        scores[system][metric].append(score)
                        row_has_score = True

            pref = row.get("best_overall_A_B_C_Tie", "").strip().upper()
            if pref in {"A", "B", "C"}:
                win_counts[key[(example_id, pref)]] += 1
            elif pref in {"TIE", "TIE / HARD TO TELL", "HARD TO TELL"}:
                tie_count += 1
            elif pref:
                raise ValueError(
                    f"Row {row_num}: best_overall_A_B_C_Tie must be A, B, C, or Tie"
                )

            if row_has_score:
                completed_rows += 1

    denominator_with_ties = sum(win_counts.values()) + tie_count
    denominator_without_ties = sum(win_counts.values())

    output_rows = []
    for system in SYSTEMS:
        output_rows.append(
            {
                "system": system,
                "meaning_mean": fmt(mean(scores[system]["meaning"])),
                "fluency_mean": fmt(mean(scores[system]["fluency"])),
                "cefr_fit_mean": fmt(mean(scores[system]["cefr_fit"])),
                "rating_count_per_metric": len(scores[system]["meaning"]),
                "overall_wins": win_counts[system],
                "win_rate_ties_excluded": fmt(
                    win_counts[system] / denominator_without_ties
                    if denominator_without_ties
                    else None
                ),
                "win_rate_ties_in_denominator": fmt(
                    win_counts[system] / denominator_with_ties
                    if denominator_with_ties
                    else None
                ),
            }
        )

    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {out_path}")
    print(f"Completed rating rows: {completed_rows}")
    print(f"Unique examples seen: {len(examples)}")
    print(f"Annotators: {', '.join(sorted(annotators)) if annotators else '(none)'}")
    print(f"Ties: {tie_count}")


if __name__ == "__main__":
    main()
