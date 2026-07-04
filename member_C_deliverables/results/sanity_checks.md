# Sanity Checks

Five identity-baseline joins were manually inspected after neural evaluation.

| ID | Target | source_id matched | Output equals source | Predicted CEFR | Confidence | MB-source | MB-reference |
|---|---|---:|---:|---|---:|---:|---:|
| 21-a2 | A2 | yes | yes | B1 | 0.9781 | 94.5269 | 58.4288 |
| 21-b1 | B1 | yes | yes | B1 | 0.9781 | 94.5269 | 85.4101 |
| 42-a2 | A2 | yes | yes | B2 | 0.9953 | 94.5268 | 73.4601 |
| 77-b1 | B1 | yes | yes | A2 | 0.9984 | 94.5269 | 90.1710 |
| 100-a2 | A2 | yes | yes | B1 | 0.9829 | 94.5269 | 93.8139 |

Checks:

- Alignment fields and score directions are correct for all five rows.
- Identity has a `source_exact_rate` of 1.0.
- MeaningBERT's native identical-text score is about 94.5, not exactly 100.
- The same identity output can legitimately score differently against the A2 and B1
  references for a shared source.
