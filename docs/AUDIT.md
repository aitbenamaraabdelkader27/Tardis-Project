# Historical repository audit — 16 October 2026

This document describes the original EPITECH working tree before the public
refactor. Paths, remotes and retention decisions below are historical, not the
current personal repository state. See [cleanup audit](CLEANUP.md) for the
19 October migration and external archive location.

Completed before implementation changes. Inspected every tracked source, notebook cell,
CSV schema, documentation file, dependency/configuration file and artifact; reviewed git status/history/remotes.
No AGENTS.md was present in the repository. Existing uncommitted changes to
`src/preprocessing.py` (comment) and `tardis_eda.ipynb` are preserved.

## Original assets and findings

- `data/project_dataset.csv`: 12,070 rows, 26 French columns, semicolon separated.
  174 exact duplicate rows; mixed date formats, decimal commas, missing values,
  malformed numbers and negative counts. Source URL/download metadata absent.
  Schema matches SNCF Voyageurs' official AQST monthly TGV route dataset.
  Its exact lineage and any educational alterations cannot be verified.
- `cleaned_dataset.csv`: 11,516 rows, 28 columns, 2018–2025; 12 exact duplicates.
  Departure column renamed to English, while training expects French. This breaks
  `python -m src.train`. Original reports describe different row counts.
- `tardis_eda.ipynb`: useful exploration by year/service; text cleanup, date parsing,
  duplicate removal, date features. Converts negative delays/counts to zero and
  loses decimal commas. Its current contents include user changes: retained intact.
- `src/features.py`: reusable cleaning intent but incomplete parsing, unvalidated
  missing dates and fragile integer conversion. Replaced with documented official-snapshot processing.
- `src/preprocessing.py`: sound ColumnTransformer/Pipeline structure with imputation,
  scaling, unknown-safe one-hot encoding. Retained and adapted.
- `tardis_model.ipynb`: linear regression and Random Forest, random 80/20 split,
  label encoders refitted per column and not saved; uses same-month cancellations
  unavailable prospectively. Broken relative dataset path. Retained as historical work.
- `src/train.py`: 400-tree Random Forest, six inputs, random split, mean baseline;
  saves complete pipeline. Same-month observed average duration is not a planned
  journey duration and cannot safely be requested as a prospective input.
- `model.joblib`: approximately 58 MB existing pipeline; legacy artifact retained.
  `models/model.joblib`: empty placeholder, unusable. Neither is used by the new demo.
- Original documented MAE 2.067 / RMSE 4.293 / R² 0.045 derive from a random split;
  not evidence for the new chronological forecast. No saved held-out predictions.
- `tardis_dashboard.py`: working Streamlit concept with overview, filters and form;
  French interface, dependent on working directory, silent model-load failures,
  invalid route combinations possible, no evaluation page, confusing monthly vs train target.
- `src/data_checks.py`: checks expect mixed column naming, prohibit all negative
  delays (early arrivals can be valid), and are not a coherent reproducible data contract.
- Tests, `src/evaluate.py`, `pyproject.toml`, `app/components/*` are empty placeholders.
- Dependencies unpinned; .streamlit and all models ignored; deployment not reproducible.
- No assignment PDF, paid service integration or credentials found in tracked sources.
  No license for original collective code: publication rights must be confirmed by owner.
  Existing origin belongs to EpitechBachelorPromo2028, not a verified personal repository.

## Decision

Keep original CSVs, notebooks, reports and model as historical evidence; do not
claim questionable raw values are authenticated observations. Fetch an official
2018–2025 snapshot into a separate file, with metadata, checksum and ODbL attribution.
No synthetic data. Predict monthly route average arrival delay in minutes, using
service, origin, destination, year and month. Exclude contemporaneous operational
measurements, including duration, cancellations, cause percentages and delay counts.
Reserve 2024 for validation/model selection and 2025 for final evaluation; train
candidates on 2018–2023, then refit selected candidate on 2018–2024 for the saved demo.
Compare mean and route historical-mean baselines and Random Forest without tuning on test.
Report all candidate scores and preserve the measured predictions. Do not deploy or push.
