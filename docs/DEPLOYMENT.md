# Public release and deployment

The personal repository is already initialised on `main`, with origin
`git@github.com:aitbenamaraabdelkader27/Tardis-Project.git`.
The historical EPITECH repository is archived outside this working tree. Its
remote was not changed. No commit, push or deployment was performed.

## Prepare a reviewable public release

1. Confirm collective-code redistribution rights and team attribution. The official
   SNCF snapshot has separate ODbL attribution; see `THIRD_PARTY_NOTICES.md`.
2. Review `git diff --cached --stat` and `git diff --cached --name-status`.
   Historical coursework, virtual environments and secrets must remain excluded.
3. Use Python 3.12, install `requirements.txt`, run
   `python -m unittest discover -s tests -v` and
   `python -m streamlit run tardis_dashboard.py`.
4. Commit and push to the personal origin only after explicit authorisation.
   An optional fresh export can be made with
   `python scripts/prepare_public_release.py --output /tmp/tardis-public-reviewed`.
   The script refuses existing destinations and does not establish publication rights.

## Deploy on Streamlit Community Cloud

Follow the current [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

1. After explicit deployment authorisation, sign in at https://share.streamlit.io/
   with the GitHub account that can access the prepared repository.
2. Choose **Create app**, then **Yup, I have an app** when prompted.
3. Select the personal repository, its published branch (usually `main`), and main
   file path **`tardis_dashboard.py`**. Set a free available subdomain if desired.
4. In **Advanced settings**, choose **Python 3.12**. Add **no secrets**. Save.
5. Deploy. Community Cloud installs the root `requirements.txt`. The root
   `.streamlit/config.toml` supplies the light theme. The app loads versioned data
   and the saved artifact; no training or network data retrieval is performed.
6. Check Overview KPIs and plots; Explorer station/year filters and empty state;
   Prediction with both services; Performance scores and plots. Check logs for
   exceptions, verify the app is publicly viewable, and test its URL logged out.
7. Record the **actual** GitHub and live URLs in README and `portfolio.json`.
   Never label a proposed `streamlit.app` subdomain as already live.

## Required deployment assets

- `data/sncf_2018_2025.csv.gz` and `data/source.json`
- `models/forecast.joblib` and `models/routes.csv`
- `reports/metrics.json` and `reports/predictions.csv`
- `src/`, `app/components/`, `tardis_dashboard.py`, `requirements.txt`, `.streamlit/config.toml`

Do not omit ignored artifacts: the supported forecast artifact and config are
explicitly unignored. There is no Git LFS requirement. Large legacy models and
notebooks are not needed by the public app.

## Maintenance and troubleshooting

- Missing/checksum-mismatched dataset: restore snapshot and manifest from the same
  commit. Do not silently substitute the educational CSV.
- Artifact/version error: install the exact requirements and restore all model/report
  files from the same commit, or run `python -m src.train` locally and commit the
  resulting artifacts together. Joblib compatibility depends on the training stack.
- No matched observations: clear filters. This is a valid state, not a data error.
- No training occurs on page visits. Resource consumption is dominated by Streamlit,
  pandas, scikit-learn and Plotly rather than the 2.7 KB selected model.
- Official refresh: run `scripts/fetch_data.py` locally, review differences, retrain,
  retest and update measured results. Never trigger downloads automatically in the app.
- The supported forecast year is fixed at 2025. Extending it requires a new time
  protocol, evaluation and interface update; changing a date selector alone does
  not validate future predictions.
