# Human Evaluation Assets

This folder contains the 30-example anonymous human evaluation package.

## Files

- `human_eval_questions.csv`: anonymized examples for inspection or manual form creation.
- `human_eval_google_sheets_template.csv`: recommended Google Sheets annotation template.
- `human_eval_key_private.csv`: private A/B/C-to-system mapping. Do not share this with annotators.
- `human_eval_sample_manifest.json`: sample seed, sample size, and selected IDs.
- `create_google_form.gs`: Google Apps Script that creates the anonymous Google Form.
- `create_human_eval_assets.py`: reproducible script used to generate these files from the latest repo.
- `create_google_sheets_template.py`: regenerates the Google Sheets annotation template.
- `summarize_human_eval.py`: maps anonymous A/B/C ratings back to systems and summarizes results.

## Sample

- Total examples: 30
- A2 examples: 15
- B1 examples: 15
- Systems compared: zero-shot, three-shot, self-refine
- Random seed: 6120

## Recommended: Use Google Sheets

Use this option if Google blocks the Apps Script form generator with an unverified app warning.

1. Open Google Sheets.
2. Import `human_eval_google_sheets_template.csv`.
3. Freeze the first row.
4. Turn on text wrapping for the paragraph/output columns.
5. Add data validation for score columns:
   - `A_meaning_1_5`, `A_fluency_1_5`, `A_cefr_fit_1_5`
   - `B_meaning_1_5`, `B_fluency_1_5`, `B_cefr_fit_1_5`
   - `C_meaning_1_5`, `C_fluency_1_5`, `C_cefr_fit_1_5`
   - allowed values: whole number from 1 to 5
6. Add data validation for `best_overall_A_B_C_Tie`:
   - dropdown values: `A`, `B`, `C`, `Tie`
7. Share a separate copy or tab with each annotator.

Keep `human_eval_key_private.csv` private. Annotators should never see the real
system names.

## Summarize Filled Ratings

After annotators finish:

1. Combine all completed rows into one sheet.
2. Export the combined sheet as CSV, for example:
   - `human_eval_filled.csv`
3. Save it in this folder.
4. Run:

```bash
python3 human_evaluation/summarize_human_eval.py human_evaluation/human_eval_filled.csv
```

The script writes:

- `human_eval_summary_by_system.csv`

Use that summary table in the final paper.

## Optional: Create the Google Form

The Apps Script option is still available, but Google may show an unverified-app
warning.

1. Open https://script.google.com/.
2. Create a new project.
3. Copy the full contents of `create_google_form.gs` into the editor.
4. Run `createHumanEvaluationForm`.
5. Approve permissions if you choose to proceed.
6. Open the logged Form edit URL, public URL, and response sheet URL.

## Annotator Instructions

Ask each annotator to:

- Enter only an anonymous annotator ID, such as `A1`, `A2`, or `A3`.
- Rate each output on:
  - meaning preservation
  - fluency
  - CEFR fit
- Choose the best overall output for each example.
- Avoid editing or rewriting the model outputs.

## Paper Note

Report this as a small-scale human evaluation. Do not make strong claims if only one
annotator completes the form.
