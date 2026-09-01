import pandas as pd


def build_document_features(
    documents: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create numerical features used by the
    financial anomaly models.
    """

    if documents.empty:
        return documents.copy()

    df = documents.copy()

    numeric_columns = [
        "subtotal",
        "tax_amount",
        "total_amount",
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Tax as a percentage of subtotal.
    df["tax_ratio"] = (
        df["tax_amount"]
        / df["subtotal"].replace(0, pd.NA)
    )

    df["tax_ratio"] = (
        df["tax_ratio"]
        .fillna(0)
        .astype(float)
    )

    # Difference between subtotal + tax
    # and the reported total.
    df["calculated_total"] = (
        df["subtotal"]
        + df["tax_amount"]
    )

    df["total_difference"] = (
        df["total_amount"]
        - df["calculated_total"]
    )

    # Useful for identifying unusually
    # large transactions.
    df["log_total_amount"] = (
        (df["total_amount"].clip(lower=0) + 1)
        .apply(__import__("math").log1p)
    )

    return df