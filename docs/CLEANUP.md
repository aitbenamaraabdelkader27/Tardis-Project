# Personal repository cleanup — 19 October 2026

## Scope and preserved work

The personal working tree is `/home/abdelkader/Tardis-Project`, branch `main`.
Origin remains `git@github.com:aitbenamaraabdelkader27/Tardis-Project.git`.
The main `.git` is retained. The already-staged deletion of the EPITECH gitlink
is retained; the next commit will contain ordinary project files.
The existing personal HEAD contains only that historical gitlink, not the private
repository object history. No history rewrite, commit, push or deployment occurred.

Compared all files against `/tmp/tardis-public`: shared files were identical;
its only additional files were Python bytecode caches. Kept the matching public
refactor, then updated repository-specific docs, metadata and ignore rules.
Preserved all supported modules, four-page Streamlit dashboard, Plotly charts,
11,818-row official SNCF snapshot, model, reports, 17 tests and screenshots.
No scientific inputs, model-selection rules or scores were edited.

## External backup

Durable local backup, created without overwriting an existing directory:
`/home/abdelkader/Tardis-Project-backup-20261019-104355/`.

Moved the entire `B-DAT-200-PAR-2-1-tardis-8/` there, including its private Git
history, unchanged origin configuration, virtual environment and local edits.
Also moved root historical CSVs, both notebooks, the 57,955,144-byte model,
`models/model.joblib` (empty placeholder), `data/project_dataset.csv`,
`docs/legacy/`, old `DATA_DICTIONNARY.md`, `EDA_INSIGHTS.md`, `MODEL_REPORT.md`,
and the empty unused `app/components/sidebar.py`.
The backup has a SHA-256 manifest for individually moved files. Root CSVs,
notebooks and large model matched their nested-repository copies before moving.
Nothing useful was deleted; historical files are excluded from the personal tree.
The existing public export under `/tmp` was not modified.

## Security and publication

Scanned all retained text for common GitHub/OpenAI/AWS token patterns, private-key
headers and quoted secret assignments: no matches. No `.env`, `secrets.toml`,
private-key or credential file was found among release candidates. Dataset schema
contains railway monthly aggregates and descriptive comments; email-pattern scan
of all field values found none. This is a heuristic check, not proof that every
free-text comment is devoid of personal information.
Largest release file is the 752,669-byte official compressed data snapshot.
No virtual environment, cache, historical model or private Git objects are included.
Ignore rules cover accidental coursework imports, secrets and local tooling.

Collective-code redistribution rights and individual/team attribution remain
unverified. The owner must confirm these before making the repository public.
No assignment statements or grading materials were found in retained files.
No blanket software license was added. SNCF ODbL attribution and database
redistribution requirements remain in `THIRD_PARTY_NOTICES.md`.
The private EPITECH remote was never contacted or modified.

## Validation

- Python 3.12.3 in `/tmp/tardis-runtime-venv`; `pip check` passed.
- `python -m unittest discover -s tests -v`: 17 tests passed after cleanup.
  Covers all four pages, Plotly, both services, prediction, data checksum,
  saved model/reports, chronology and expected missing-artifact handling.
- Streamlit started on loopback port 8502; health returned `ok` and root HTTP 200.
- Community Cloud layout follows the official deployment documentation:
  https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
  Root requirements/config, Python 3.12, versioned runtime assets and repository-
  relative paths are retained. Hosting was not provisioned or tested remotely.
- Re-ran `python -m src.train`: model, routes, metrics and predictions were
  byte-identical (SHA-256 before/after in `/tmp/tardis-cleanup-repro.json`).
- Final index uses the public-release allowlist. It contains no gitlink, nested
  repository, caches, credentials or large historical artifacts.
- The temporary local verification server was stopped after the HTTP checks.

## Review before committing

Run `git diff --cached --name-status`, `git diff --cached --stat` and
`git diff --cached --check`. Confirm redistribution rights before publication.
Only after authorisation:

```bash
cd /home/abdelkader/Tardis-Project
git commit -m "Restructure TARDIS portfolio repository and preserve reproducible dashboard"
git push -u origin main
```
