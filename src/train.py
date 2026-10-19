"""Reproduce candidate selection, held-out scores and the complete demo artifact."""
import hashlib
import importlib.metadata
import json
import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from src.config import DATA_PATH, FEATURE_COLS, MODEL_PATH, REPORT_PATH, ROUTE_COLS, TARGET_COL
from src.data import eligible_rows, load_dataset, quality_report
from src.evaluate import regression_metrics
from src.features import CalendarFeatures, RouteMeanRegressor
from src.preprocessing import build_pipeline


def candidates():
    return {
        "Global mean": build_pipeline(None, DummyRegressor(strategy="mean")),
        "Route historical mean": Pipeline([("calendar", CalendarFeatures()), ("model", RouteMeanRegressor())]),
        "Random Forest": build_pipeline(None, RandomForestRegressor(
            n_estimators=160, max_depth=14, min_samples_leaf=5,
            max_features=0.8, random_state=42, n_jobs=1)),
    }


def main():
    raw = load_dataset()
    data = raw.loc[eligible_rows(raw)].copy()
    training = data[data.Date < "2024-01-01"]
    validation = data[data.Date.between("2024-01-01", "2024-12-01")]
    development = data[data.Date < "2025-01-01"]
    test = data[data.Date >= "2025-01-01"]
    assert training.Date.max() < validation.Date.min() < test.Date.min()
    validation_scores, test_scores = {}, {}
    heldout = test[["Date", *ROUTE_COLS, TARGET_COL]].rename(columns={TARGET_COL: "actual"}).copy()
    fitted = {}
    models = candidates()
    for name, pipeline in models.items():
        pipeline.fit(training[FEATURE_COLS], training[TARGET_COL])
        validation_scores[name] = regression_metrics(validation[TARGET_COL], pipeline.predict(validation[FEATURE_COLS]))
    selected = min(validation_scores, key=lambda name: validation_scores[name]["MAE"])
    # Selection is locked before any test predictions are inspected.
    for name, pipeline in candidates().items():
        pipeline.fit(development[FEATURE_COLS], development[TARGET_COL])
        predicted = pipeline.predict(test[FEATURE_COLS])
        test_scores[name] = regression_metrics(test[TARGET_COL], predicted)
        heldout[name] = predicted
        fitted[name] = pipeline
    MODEL_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(fitted[selected], MODEL_PATH, compress=3)
    routes = development.groupby(ROUTE_COLS, as_index=False).size().rename(columns={"size": "training_months"})
    routes.to_csv(MODEL_PATH.with_name("routes.csv"), index=False)
    heldout.to_csv(REPORT_PATH.with_name("predictions.csv"), index=False, float_format="%.12g")
    report = {
        "task": "Monthly route mean arrival delay regression", "unit": "minutes",
        "features": FEATURE_COLS, "engineered_features": [*ROUTE_COLS, "Year", "Month_sin", "Month_cos"],
        "seed": 42, "selection_rule": "Lowest 2024 validation MAE; no test tuning",
        "selected_model": selected, "validation": validation_scores, "test": test_scores,
        "periods": {name: {"start": str(frame.Date.min().date()), "end": str(frame.Date.max().date()), "rows": len(frame)}
                    for name, frame in [("training", training), ("validation", validation), ("artifact_training", development), ("test", test)]},
        "quality": quality_report(raw),
        "dataset_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        "model_sha256": hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest(),
        "routes_sha256": hashlib.sha256(MODEL_PATH.with_name("routes.csv").read_bytes()).hexdigest(),
        "predictions_sha256": hashlib.sha256(REPORT_PATH.with_name("predictions.csv").read_bytes()).hexdigest(),
        "versions": {p: importlib.metadata.version(p) for p in ["pandas", "numpy", "scikit-learn", "joblib"]},
        "random_forest_parameters": models["Random Forest"].named_steps["model"].get_params(),
        "test_unseen_routes": int(sum(tuple(row) not in set(development[ROUTE_COLS].itertuples(index=False, name=None))
                                      for row in test[ROUTE_COLS].itertuples(index=False, name=None))),
        "test_target_negative_rows": int((test[TARGET_COL] < 0).sum()),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"selected": selected, "validation": validation_scores, "test": test_scores,
                      "rows": report["periods"], "model_bytes": MODEL_PATH.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
