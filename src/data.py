"""Official data contract. Preserve signed delays and report source anomalies."""
import gzip
import hashlib
import json
import numpy as np
import pandas as pd
from src.config import DATA_PATH, ROUTE_COLS, TARGET_COL


def load_dataset(path=DATA_PATH):
    manifest = json.loads(DATA_PATH.with_name("source.json").read_text())
    raw = gzip.decompress(path.read_bytes())
    if hashlib.sha256(raw).hexdigest() != manifest["sha256_uncompressed"]:
        raise ValueError("Dataset checksum mismatch. Restore the versioned SNCF snapshot.")
    import io
    df = pd.read_csv(io.BytesIO(raw), sep=";")
    labels = {f["name"]: f["label"] for f in manifest["fields"]}
    df = df.rename(columns=labels)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m", errors="coerce")
    for col in ROUTE_COLS:
        df[col] = df[col].str.strip().replace("", np.nan)
    for f in manifest["fields"]:
        if f["type"] in ("int", "double"):
            col = f["label"]
            df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    if df.duplicated(["Date", *ROUTE_COLS]).any():
        raise ValueError("Ambiguous duplicate route-months in official snapshot.")
    df["Year"] = df.Date.dt.year
    df["Month"] = df.Date.dt.month
    return df.sort_values(["Date", *ROUTE_COLS]).reset_index(drop=True)


def eligible_rows(df):
    """Predefined eligibility; never infer or repair an observed target."""
    return (
        df[["Date", *ROUTE_COLS, TARGET_COL]].notna().all(axis=1)
        & (df["Nombre de circulations prévues"] > df["Nombre de trains annulés"])
        & (df["Nombre de trains annulés"] >= 0)
    )


def quality_report(df):
    return {
        "raw_rows": len(df), "eligible_rows": int(eligible_rows(df).sum()),
        "excluded_rows": int((~eligible_rows(df)).sum()),
        "missing_by_column": df.isna().sum().astype(int).to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "duplicate_route_months": int(df.duplicated(["Date", *ROUTE_COLS]).sum()),
        "negative_target_rows": int((df[TARGET_COL] < 0).sum()),
        "target_below_minus_30_min": int((df[TARGET_COL] < -30).sum()),
        "negative_count_cells": int(df.filter(regex="^Nombre").lt(0).sum().sum()),
        "policy": "Exclude missing identity/target and no operated trains. Retain signed delays, including source anomalies. Never clip targets or impute outcomes.",
    }
