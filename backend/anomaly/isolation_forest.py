from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyResult:

    is_anomaly: bool

    anomaly_score: float

    risk_level: str


class FinancialIsolationForest:
    """
    Detects unusual financial transactions
    using Isolation Forest.
    """

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ):

        self.model = IsolationForest(

            contamination=contamination,

            random_state=random_state,

            n_estimators=200,
        )

        self.feature_columns: list[str] = []

        self.is_fitted = False

    def fit(
        self,
        data: pd.DataFrame,
        feature_columns: list[str],
    ):

        if data.empty:
            raise ValueError(
                "Cannot train Isolation Forest "
                "on an empty dataset."
            )

        missing = set(
            feature_columns
        ) - set(data.columns)

        if missing:

            raise ValueError(
                f"Missing features: {missing}"
            )

        X = data[
            feature_columns
        ].copy()

        X = X.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        X = X.fillna(0)

        self.model.fit(X)

        self.feature_columns = (
            feature_columns
        )

        self.is_fitted = True

        return self

    def predict(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:

        if not self.is_fitted:

            raise RuntimeError(
                "Model must be fitted before "
                "prediction."
            )

        X = data[
            self.feature_columns
        ].copy()

        X = X.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        X = X.fillna(0)

        predictions = (
            self.model.predict(X)
        )

        scores = (
            self.model.decision_function(X)
        )

        result = data.copy()

        result["is_anomaly"] = (
            predictions == -1
        )

        result["anomaly_score"] = (
            -scores
        )

        result["risk_level"] = (
            result["anomaly_score"]
            .apply(
                self._risk_level
            )
        )

        return result

    @staticmethod
    def _risk_level(
        score: float,
    ) -> str:

        if score >= 0.25:

            return "HIGH"

        if score >= 0.10:

            return "MEDIUM"

        return "LOW"