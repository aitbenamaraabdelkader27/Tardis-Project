"""Load versioned artifacts and guard the supported demonstration domain."""
import hashlib
import importlib.metadata
import json
import joblib
import pandas as pd
from src.config import DATA_PATH, MODEL_PATH, REPORT_PATH, ROUTE_COLS


def load_artifacts():
    report = json.loads(REPORT_PATH.read_text())
    for path, key in [(MODEL_PATH, "model_sha256"), (DATA_PATH, "dataset_sha256"),
                      (MODEL_PATH.with_name("routes.csv"), "routes_sha256"),
                      (REPORT_PATH.with_name("predictions.csv"), "predictions_sha256")]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != report[key]:
            raise ValueError(f"Version mismatch for {path.name}. Restore matching data, report and model.")
    for package, version in report["versions"].items():
        if importlib.metadata.version(package) != version:
            raise ValueError(f"{package} must be {version}. Install requirements.txt.")
    return joblib.load(MODEL_PATH), report, pd.read_csv(MODEL_PATH.with_name("routes.csv"))


def predict_month(model, routes, service, departure, arrival, month):
    date = pd.Timestamp(month)
    if date.year != 2025 or date.day != 1:
        raise ValueError("This frozen evaluation demo supports monthly forecasts for 2025 only.")
    selected = routes[(routes[ROUTE_COLS] == [service, departure, arrival]).all(axis=1)]
    if selected.empty:
        raise ValueError("Choose a route observed during training.")
    row = pd.DataFrame([dict(zip(ROUTE_COLS, [service, departure, arrival])) | {"Date": date}])
    return float(model.predict(row)[0])
