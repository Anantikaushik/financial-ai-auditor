import pandas as pd

from backend.anomaly.isolation_forest import (
    FinancialIsolationForest,
)


def test_isolation_forest():

    data = pd.DataFrame(
        {
            "total_amount": [
                100,
                105,
                110,
                98,
                102,
                108,
                5000,
            ],

            "quantity": [
                1,
                2,
                1,
                2,
                1,
                2,
                50,
            ],

            "unit_price": [
                100,
                52,
                110,
                49,
                102,
                54,
                100,
            ],
        }
    )

    model = (
        FinancialIsolationForest(
            contamination=0.15
        )
    )

    model.fit(
        data,
        [
            "total_amount",
            "quantity",
            "unit_price",
        ],
    )

    result = model.predict(
        data
    )

    assert (
        "is_anomaly"
        in result.columns
    )

    assert (
        "anomaly_score"
        in result.columns
    )

    assert (
        "risk_level"
        in result.columns
    )

    assert len(result) == 7