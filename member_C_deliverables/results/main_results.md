# Main Results

Backend: `neural`.

| System | Target | N | CEFR exact acc. | CEFR RMSE | MB-source | MB-reference | Mean revisions |
|---|---|---|---|---|---|---|---|
| identity | ALL | 200 | 0.2650 | 1.3266 | 94.4612 | 81.4519 | 0.0000 |
| identity | A2 | 100 | 0.0800 | 1.6523 | 94.4612 | 78.0577 | 0.0000 |
| identity | B1 | 100 | 0.4500 | 0.8888 | 94.4612 | 84.8461 | 0.0000 |
| human_reference_oracle | ALL | 200 | 0.6250 | 0.6124 | 80.8381 | 94.4064 | 0.0000 |
| human_reference_oracle | A2 | 100 | 0.6400 | 0.6000 | 77.1183 | 94.5118 | 0.0000 |
| human_reference_oracle | B1 | 100 | 0.6100 | 0.6245 | 84.5580 | 94.3011 | 0.0000 |
| open_model_zero_shot | ALL | 200 | 0.1650 | 1.5264 | 82.7452 | 76.2837 | 0.0000 |
| open_model_zero_shot | A2 | 100 | 0.1200 | 1.8655 | 83.0823 | 72.4056 | 0.0000 |
| open_model_zero_shot | B1 | 100 | 0.2100 | 1.0863 | 82.4082 | 80.1618 | 0.0000 |
| open_model_three_shot | ALL | 200 | 0.2000 | 1.4440 | 84.9343 | 76.4815 | 0.0000 |
| open_model_three_shot | A2 | 100 | 0.0800 | 1.7607 | 84.0336 | 73.1320 | 0.0000 |
| open_model_three_shot | B1 | 100 | 0.3200 | 1.0344 | 85.8349 | 79.8309 | 0.0000 |
| open_model_self_refine | ALL | 200 | 0.1750 | 1.5149 | 82.8383 | 76.3992 | 1.0350 |
| open_model_self_refine | A2 | 100 | 0.1200 | 1.8762 | 82.7080 | 72.4996 | 0.6500 |
| open_model_self_refine | B1 | 100 | 0.2300 | 1.0344 | 82.9687 | 80.2987 | 1.4200 |
