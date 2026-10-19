"""Fetch the official, bounded snapshot; never called by the dashboard."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_PATH

BASE = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/regularite-mensuelle-tgv-aqst"
URL = BASE + "/exports/csv?" + urlencode({
    "where": 'date >= "2018-01-01" and date < "2026-01-01"',
    "order_by": "date,service,gare_depart,gare_arrivee", "use_labels": "false", "delimiter": ";"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-file", type=Path, help="Already downloaded official CSV")
    parser.add_argument("--metadata-file", type=Path)
    args = parser.parse_args()
    raw = args.from_file.read_bytes() if args.from_file else urlopen(URL, timeout=90).read()
    metadata = json.loads(args.metadata_file.read_text()) if args.metadata_file else json.load(urlopen(BASE, timeout=45))
    import pandas as pd
    data = pd.read_csv(io.BytesIO(raw), sep=";")
    assert {"date", "gare_depart", "gare_arrivee", "retard_moyen_tous_trains_arrivee"} <= set(data.columns)
    dates = pd.to_datetime(data.date, format="%Y-%m")
    assert dates.between("2018-01-01", "2025-12-01").all()
    DATA_PATH.parent.mkdir(exist_ok=True)
    DATA_PATH.write_bytes(gzip.compress(raw, mtime=0))
    manifest = {
        "publisher": "SNCF Voyageurs", "dataset": metadata["dataset_id"],
        "source_url": "https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/",
        "download_url": URL, "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "license": metadata["metas"]["default"]["license"],
        "license_url": metadata["metas"]["default"]["license_url"],
        "sha256_uncompressed": hashlib.sha256(raw).hexdigest(),
        "rows": len(data), "period_start": str(data.date.min()), "period_end": str(data.date.max()),
        "fields": metadata["fields"], "source_metadata": metadata["metas"]["default"],
    }
    DATA_PATH.with_name("source.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {len(data):,} official rows to {DATA_PATH.name} ({DATA_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
