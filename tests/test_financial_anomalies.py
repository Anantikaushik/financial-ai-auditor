import pandas as pd

from backend.anomaly.features import (
    build_document_features,
)

from backend.anomaly.duplicates import (
    detect_duplicate_invoices,
)


def test_feature_engineering():

    data = pd.DataFrame(
        {
            "subtotal": [1000, 2000],
            "tax_amount": [180, 360],
            "total_amount": [1180, 2360],
        }
    )

    result = build_document_features(
        data
    )

    assert "tax_ratio" in result.columns

    assert (
        "total_difference"
        in result.columns
    )

    assert (
        "log_total_amount"
        in result.columns
    )

    assert (
        abs(result.iloc[0]["tax_ratio"] - 0.18)
        < 0.001
    )

    assert (
        result.iloc[0]["total_difference"]
        == 0
    )


def test_duplicate_detection():

    data = pd.DataFrame(
        {
            "vendor_name": [
                "ABC Ltd",
                "ABC Ltd",
                "XYZ Ltd",
            ],
            "invoice_number": [
                "INV-001",
                "INV-001",
                "INV-002",
            ],
            "total_amount": [
                10000,
                10000,
                20000,
            ],
        }
    )

    result = detect_duplicate_invoices(
        data
    )

    assert (
        result["is_duplicate"].tolist()
        == [True, True, False]
    )