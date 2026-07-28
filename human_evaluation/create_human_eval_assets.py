from __future__ import annotations

import csv
import json
import random
from pathlib import Path


ROOT = Path("/private/tmp/NLP-Project-human-eval")
OUT = Path(__file__).resolve().parent
SEED = 6120
N_PER_LEVEL = 15

INPUTS = ROOT / "member_A_deliverables/data/processed/generation_inputs.jsonl"
PREDICTIONS = {
    "zero_shot": ROOT / "member_B_deliverables/predictions/zero_shot.jsonl",
    "three_shot": ROOT / "member_B_deliverables/predictions/three_shot.jsonl",
    "self_refine": ROOT / "member_B_deliverables/predictions/self_refine.jsonl",
}


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def clean_cell(text: str) -> str:
    return " ".join(str(text).split())


def main() -> None:
    rng = random.Random(SEED)

    inputs = {
        row["id"]: row
        for row in read_jsonl(INPUTS)
        if row.get("split") == "test"
    }
    predictions = {
        name: {row["id"]: row for row in read_jsonl(path)}
        for name, path in PREDICTIONS.items()
    }

    common_ids = sorted(
        set(inputs)
        .intersection(*(set(rows) for rows in predictions.values()))
    )
    by_level = {"A2": [], "B1": []}
    for example_id in common_ids:
        level = inputs[example_id]["target_level"]
        if level in by_level:
            by_level[level].append(example_id)

    selected_ids: list[str] = []
    for level in ("A2", "B1"):
        ids = by_level[level]
        if len(ids) < N_PER_LEVEL:
            raise ValueError(f"Need {N_PER_LEVEL} {level} examples, found {len(ids)}")
        selected_ids.extend(sorted(rng.sample(ids, N_PER_LEVEL)))

    # Interleave levels to make the form less monotonous, while remaining reproducible.
    a2_ids = [i for i in selected_ids if inputs[i]["target_level"] == "A2"]
    b1_ids = [i for i in selected_ids if inputs[i]["target_level"] == "B1"]
    ordered_ids = [item for pair in zip(a2_ids, b1_ids) for item in pair]

    question_rows: list[dict] = []
    key_rows: list[dict] = []
    examples_for_script: list[dict] = []
    systems = list(PREDICTIONS.keys())

    for form_index, example_id in enumerate(ordered_ids, start=1):
        item = inputs[example_id]
        labels = ["A", "B", "C"]
        shuffled = systems[:]
        rng.shuffle(shuffled)
        output_by_label = {
            label: predictions[system][example_id]["output"]
            for label, system in zip(labels, shuffled)
        }
        system_by_label = dict(zip(labels, shuffled))

        question_row = {
            "form_item": form_index,
            "example_id": example_id,
            "source_id": item["source_id"],
            "target_cefr": item["target_level"],
            "original_paragraph": clean_cell(item["source"]),
            "output_A": clean_cell(output_by_label["A"]),
            "output_B": clean_cell(output_by_label["B"]),
            "output_C": clean_cell(output_by_label["C"]),
        }
        key_row = {
            "form_item": form_index,
            "example_id": example_id,
            "source_id": item["source_id"],
            "target_cefr": item["target_level"],
            "output_A_system": system_by_label["A"],
            "output_B_system": system_by_label["B"],
            "output_C_system": system_by_label["C"],
        }

        question_rows.append(question_row)
        key_rows.append(key_row)
        examples_for_script.append(
            {
                "formItem": form_index,
                "exampleId": example_id,
                "targetCefr": item["target_level"],
                "originalParagraph": clean_cell(item["source"]),
                "outputs": {
                    "A": clean_cell(output_by_label["A"]),
                    "B": clean_cell(output_by_label["B"]),
                    "C": clean_cell(output_by_label["C"]),
                },
            }
        )

    OUT.mkdir(exist_ok=True)
    with (OUT / "human_eval_questions.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(question_rows[0]))
        writer.writeheader()
        writer.writerows(question_rows)

    with (OUT / "human_eval_key_private.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    with (OUT / "human_eval_sample_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "seed": SEED,
                "sample_size": len(ordered_ids),
                "n_per_level": N_PER_LEVEL,
                "levels": ["A2", "B1"],
                "systems": systems,
                "selected_ids": ordered_ids,
            },
            f,
            indent=2,
        )
        f.write("\n")

    script = make_apps_script(examples_for_script)
    (OUT / "create_google_form.gs").write_text(script, encoding="utf-8")


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def make_apps_script(examples: list[dict]) -> str:
    examples_json = json.dumps(examples, ensure_ascii=False, indent=2)
    return f"""// Human evaluation Google Form generator.
// Usage:
// 1. Go to https://script.google.com/
// 2. Create a new project.
// 3. Paste this entire file.
// 4. Run createHumanEvaluationForm().
// 5. Authorize the script.
// 6. Open the logged Form edit URL and Response Sheet URL.

const EXAMPLES = {examples_json};

function createHumanEvaluationForm() {{
  const form = FormApp.create('TSAR 2025 Human Evaluation - Anonymous Outputs');
  form.setDescription(
    'Please rate anonymized simplification outputs. Do not edit the outputs. ' +
    'System names are hidden. Use 1 = poor and 5 = excellent.'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);
  form.setProgressBar(true);
  form.setShuffleQuestions(false);

  form.addTextItem()
    .setTitle('Annotator ID')
    .setHelpText('Use a short anonymous label, such as A1, A2, or A3.')
    .setRequired(true);

  const scale = ['1', '2', '3', '4', '5'];
  const ratingRows = ['Meaning preservation', 'Fluency', 'CEFR fit'];
  const preferenceChoices = ['Output A', 'Output B', 'Output C', 'Tie / hard to tell'];

  EXAMPLES.forEach((example) => {{
    form.addPageBreakItem()
      .setTitle('Example ' + example.formItem + ' (' + example.exampleId + ')');

    form.addSectionHeaderItem()
      .setTitle('Original paragraph')
      .setHelpText(example.originalParagraph);

    form.addSectionHeaderItem()
      .setTitle('Target CEFR')
      .setHelpText(example.targetCefr);

    ['A', 'B', 'C'].forEach((label) => {{
      form.addSectionHeaderItem()
        .setTitle('Output ' + label)
        .setHelpText(example.outputs[label]);

      form.addGridItem()
        .setTitle('Rate Output ' + label)
        .setRows(ratingRows)
        .setColumns(scale)
        .setRequired(true);
    }});

    form.addMultipleChoiceItem()
      .setTitle('Best overall output for Example ' + example.formItem)
      .setChoiceValues(preferenceChoices)
      .setRequired(true);

    form.addParagraphTextItem()
      .setTitle('Optional notes for Example ' + example.formItem)
      .setRequired(false);
  }});

  const sheet = SpreadsheetApp.create('TSAR 2025 Human Evaluation Responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  Logger.log('Form edit URL: ' + form.getEditUrl());
  Logger.log('Form public URL: ' + form.getPublishedUrl());
  Logger.log('Response Sheet URL: ' + sheet.getUrl());
}}
"""


if __name__ == "__main__":
    main()
