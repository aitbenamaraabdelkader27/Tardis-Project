"""Calendar features computed inside the serialized forecasting pipeline."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from src.config import FEATURE_COLS, ROUTE_COLS


class CalendarFeatures(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        self.transform(X)
        self.feature_names_in_ = np.array(FEATURE_COLS, dtype=object)
        self.n_features_in_ = len(FEATURE_COLS)
        return self

    def transform(self, X):
        missing = set(FEATURE_COLS) - set(X.columns)
        if missing:
            raise ValueError(f"Missing prediction columns: {sorted(missing)}")
        dates = pd.to_datetime(X["Date"], errors="coerce")
        if dates.isna().any():
            raise ValueError("Prediction month must be a valid date.")
        result = X[ROUTE_COLS].copy()
        for col in ROUTE_COLS:
            result[col] = result[col].map(lambda v: v.strip() if isinstance(v, str) else np.nan).replace("", np.nan)
        result["Year"] = dates.dt.year.astype(float)
        result["Month_sin"] = np.sin(2 * np.pi * dates.dt.month / 12)
        result["Month_cos"] = np.cos(2 * np.pi * dates.dt.month / 12)
        return result


class RouteMeanRegressor(RegressorMixin, BaseEstimator):
    """Historical training route mean, global mean for unseen routes."""
    def fit(self, X, y):
        data = X[ROUTE_COLS].copy()
        data["target"] = np.asarray(y)
        self.global_mean_ = float(np.mean(y))
        self.route_means_ = data.groupby(ROUTE_COLS)["target"].mean().to_dict()
        return self

    def predict(self, X):
        check_is_fitted(self, "route_means_")
        return np.array([self.route_means_.get(tuple(row), self.global_mean_)
                         for row in X[ROUTE_COLS].itertuples(index=False, name=None)])
