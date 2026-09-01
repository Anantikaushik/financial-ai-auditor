import pandas as pd


def detect_duplicate_invoices(
    documents: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect duplicate invoices using:
    vendor + invoice number + total amount.
    """

    if documents.empty:

        result = documents.copy()

        result["is_duplicate"] = pd.Series(
            dtype=bool
        )

        return result

    df = documents.copy()

    required_columns = [
        "vendor_name",
        "invoice_number",
        "total_amount",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    df["is_duplicate"] = (
        df.duplicated(
            subset=required_columns,
            keep=False,
        )
    )

    return df