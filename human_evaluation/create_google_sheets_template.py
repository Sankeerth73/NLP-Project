from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUESTIONS = ROOT / "human_eval_questions.csv"
OUT = ROOT / "human_eval_google_sheets_template.csv"


FIELDS = [
    "annotator_id",
    "form_item",
    "example_id",
    "target_cefr",
    "original_paragraph",
    "output_A",
    "A_meaning_1_5",
    "A_fluency_1_5",
    "A_cefr_fit_1_5",
    "output_B",
    "B_meaning_1_5",
    "B_fluency_1_5",
    "B_cefr_fit_1_5",
    "output_C",
    "C_meaning_1_5",
    "C_fluency_1_5",
    "C_cefr_fit_1_5",
    "best_overall_A_B_C_Tie",
    "notes",
]


def main() -> None:
    with QUESTIONS.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    output_rows = []
    for row in rows:
        output_rows.append(
            {
                "annotator_id": "",
                "form_item": row["form_item"],
                "example_id": row["example_id"],
                "target_cefr": row["target_cefr"],
                "original_paragraph": row["original_paragraph"],
                "output_A": row["output_A"],
                "A_meaning_1_5": "",
                "A_fluency_1_5": "",
                "A_cefr_fit_1_5": "",
                "output_B": row["output_B"],
                "B_meaning_1_5": "",
                "B_fluency_1_5": "",
                "B_cefr_fit_1_5": "",
                "output_C": row["output_C"],
                "C_meaning_1_5": "",
                "C_fluency_1_5": "",
                "C_cefr_fit_1_5": "",
                "best_overall_A_B_C_Tie": "",
                "notes": "",
            }
        )

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    main()
