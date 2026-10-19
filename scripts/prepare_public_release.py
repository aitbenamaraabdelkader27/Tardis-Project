"""Copy an explicit public-demo allowlist, without git history or legacy coursework.

This prepares local files only. It never creates a remote, pushes or deploys.
The owner must verify rights to collective code before publication.
"""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "README.md", "THIRD_PARTY_NOTICES.md", "portfolio.json", "requirements.txt",
    "requirements-dev.txt", "requirements.lock.txt", "pyproject.toml", ".gitignore", ".streamlit/config.toml",
    "tardis_dashboard.py", "data/sncf_2018_2025.csv.gz", "data/source.json", "data/README.md",
    "models/forecast.joblib", "models/routes.csv", "reports/metrics.json", "reports/predictions.csv",
    "src/config.py", "src/data.py", "src/data_checks.py", "src/features.py",
    "src/preprocessing.py", "src/train.py", "src/evaluate.py", "src/inference.py",
    "app/components/charts.py", "app/components/helpers.py",
    "tests/test_data_checks.py", "tests/test_preprocessing.py", "tests/test_dashboard.py",
    "scripts/fetch_data.py", "scripts/prepare_public_release.py",
    "docs/AUDIT.md", "docs/CLEANUP.md", "docs/DEPLOYMENT.md", "docs/DASHBOARD_GUIDE.md", "docs/VALIDATION.md",
    "docs/screenshots/overview.png", "docs/screenshots/explorer.png",
    "docs/screenshots/prediction.png", "docs/screenshots/performance.png", "docs/screenshots/mobile.png",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="A new directory; existing paths are refused")
    output = parser.parse_args().output.resolve()
    if output.exists():
        parser.error("Output already exists. Choose a new directory; no files were overwritten.")
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        parser.error(f"Required release files missing: {missing}")
    output.mkdir(parents=True)
    for name in FILES:
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    print(f"Prepared {len(FILES)} files in {output}. No git operations or deployment performed.")
    print("Review collective-code rights and attribution before publication.")


if __name__ == "__main__":
    main()
