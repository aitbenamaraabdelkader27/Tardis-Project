# Validation record — 16 October 2026

## Executed checks

- Installed the pinned runtime requirements in a **new Python 3.12 environment**
  under `/tmp`, independently of the original `.venv`. `pip check` passed.
  Resolved runtime dependencies are pinned in `requirements.lock.txt` and constrained
  by `requirements.txt`; notebook-only packages are not needed by the app.
- **17 unittest tests passed** in the original environment and the clean environment.
  Covers source checksum, dates, route uniqueness, dtypes/date features, eligibility,
  source anomalies retained, filters and empty results, model input allowlist,
  invalid dates/schema, unknown and missing categories, training-only route fallback,
  model inference, supported forecast-domain guards, chronological separation,
  validation-driven selection, and recalculation of every candidate's test metrics.
- Streamlit AppTest covers all four pages, Plotly element presence, dependent
  route selectors, both service types, prediction submission, filters and empty
  state. Missing-data/model failures are injected and produce actionable UI errors
  without uncaught application exceptions. Their logged tracebacks during tests are intentional.
- Launched Streamlit bound to **127.0.0.1:8501**, confirmed its health endpoint,
  visited all four pages in headless Chromium, rendered Plotly plots, submitted
  a prediction and captured five screenshots (four pages and a mobile viewport).
  **No browser page errors** or Streamlit exception panels detected.
- Inspected desktop and mobile screenshots. Histogram defaults show −5 to 40 minutes
  with an explicit excluded-view count; users can reveal the full source range.
  This is only a display choice: metrics, exports and other plots retain all eligible observations.
- Repeated `python -m src.train`; **metrics.json, predictions.csv, forecast.joblib
  and routes.csv were byte-identical**. This includes validation and test scores for
  Random Forest, even though the selected artifact is the simpler route baseline.
- Checked `git diff --check`; verified config/data/model/report assets are not ignored.
- Scanned repository text/code/notebook files (excluding environments, git internals
  and private environment directories) for common GitHub/OpenAI/AWS credential
  patterns and private-key headers: **no matches**. No secrets are required by runtime.
- A minimal public export is built from an explicit allowlist and tested separately.
  It contains no `.git`, original course CSV, notebooks, large legacy model or
  historical reports. Exporting files does not assert redistribution rights.

## Measured dataset and model

- Official source: 11,818 monthly observations, January 2018–December 2025.
- Eligible cohort: 11,745; 73 no-operated-train months excluded.
- Selection: 2024 MAE, using candidate training on 2018–2023.
- Selected route historical mean: validation MAE **2.1943 min**.
- Artifact trained through 2024. Test: 1,494 rows from 2025.
- Selected artifact test: MAE **2.6863 min**, RMSE **3.7946 min**, R² **0.2089**.
- Random Forest test: MAE **2.5694 min**, RMSE **3.6468 min**, R² **0.2693**.
- Global mean test: MAE **3.2024 min**, RMSE **4.4977 min**, R² **−0.1114**.
- Full precision, parameters, versions and checksums: `reports/metrics.json`.

## Scope of validation

These checks establish a working historical demonstration. They do not establish
individual-train accuracy, real-time availability, future-year forecasting skill,
calibrated uncertainty, or resolution of official source anomalies. Exact original
course-data lineage and individual team contributions remain unverified.

No push, remote creation or public deployment has been performed. Live hosting,
its public URL and publication rights remain to be confirmed by the owner.
