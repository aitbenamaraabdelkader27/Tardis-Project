import unittest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from src.config import FEATURE_COLS, ROUTE_COLS, TARGET_COL, REPORT_PATH
from src.data import eligible_rows, load_dataset
from src.evaluate import regression_metrics
from src.features import CalendarFeatures, RouteMeanRegressor
from src.inference import load_artifacts, predict_month
from src.preprocessing import build_pipeline


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.report, cls.routes = load_artifacts()
        raw = load_dataset()
        cls.df = raw.loc[eligible_rows(raw)]

    def test_features_are_available_before_month(self):
        self.assertEqual(FEATURE_COLS, ["Date", *ROUTE_COLS])
        x = self.df[FEATURE_COLS].head(3)
        a = CalendarFeatures().fit_transform(x)
        b = x.copy()
        b[TARGET_COL] = 99999
        b["Nombre de trains annulés"] = 99999
        pd.testing.assert_frame_equal(a, CalendarFeatures().fit_transform(b))
        self.assertTrue(np.isfinite(a.select_dtypes("number")).all().all())

    def test_invalid_schema_and_date(self):
        x = self.df[FEATURE_COLS].head(1).copy()
        with self.assertRaisesRegex(ValueError, "Missing prediction"):
            CalendarFeatures().fit_transform(x.drop(columns="Date"))
        x["Date"] = "not a month"
        with self.assertRaisesRegex(ValueError, "valid date"):
            CalendarFeatures().fit_transform(x)

    def test_unknown_and_missing_categories_do_not_crash_forest(self):
        x = self.df[FEATURE_COLS].head(100)
        pipeline = build_pipeline(x, RandomForestRegressor(n_estimators=3, random_state=42, n_jobs=1)).fit(x, self.df[TARGET_COL].head(100))
        row = x.head(2).copy()
        row.loc[row.index[0], ROUTE_COLS[1]] = "UNKNOWN STATION"
        row.loc[row.index[1], ROUTE_COLS[2]] = np.nan
        self.assertTrue(np.isfinite(pipeline.predict(row)).all())

    def test_unknown_route_uses_training_mean(self):
        x = self.df[ROUTE_COLS].head(3)
        model = RouteMeanRegressor().fit(x, [1, 2, 3])
        row = x.head(1).copy()
        row[ROUTE_COLS[1]] = "UNKNOWN"
        self.assertEqual(model.predict(row)[0], 2)

    def test_saved_model_reproduces_test_predictions_and_metrics(self):
        test = self.df[self.df.Date >= "2025-01-01"]
        pred = self.model.predict(test[FEATURE_COLS])
        recorded = pd.read_csv(REPORT_PATH.with_name("predictions.csv"))
        np.testing.assert_allclose(pred, recorded[self.report["selected_model"]], rtol=1e-10)
        for name in self.report["test"]:
            scores = regression_metrics(recorded.actual, recorded[name])
            for metric, value in scores.items():
                self.assertAlmostEqual(value, self.report["test"][name][metric], places=8)

    def test_selection_and_chronology(self):
        winner = min(self.report["validation"], key=lambda k: self.report["validation"][k]["MAE"])
        self.assertEqual(self.report["selected_model"], winner)
        p = self.report["periods"]
        self.assertLess(p["training"]["end"], p["validation"]["start"])
        self.assertLess(p["artifact_training"]["end"], p["test"]["start"])
        self.assertEqual(p["test"]["rows"], 1494)

    def test_guarded_inference(self):
        service, departure, arrival = self.routes[ROUTE_COLS].iloc[0]
        value = predict_month(self.model, self.routes, service, departure, arrival, "2025-06-01")
        self.assertTrue(np.isfinite(value))
        with self.assertRaisesRegex(ValueError, "observed during training"):
            predict_month(self.model, self.routes, service, "UNKNOWN", arrival, "2025-06-01")
        with self.assertRaisesRegex(ValueError, "2025 only"):
            predict_month(self.model, self.routes, service, departure, arrival, "2026-06-01")
