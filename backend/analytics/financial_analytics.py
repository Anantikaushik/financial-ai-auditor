from pathlib import Path

import duckdb
import pandas as pd


class FinancialAnalytics:
    """
    Read-only analytics layer for financial data.

    This class contains business analytics logic
    separately from the Streamlit UI.
    """

    def __init__(
        self,
        database_path: str | Path,
    ):

        self.database_path = Path(
            database_path
        )

    def _connect(self):

        return duckdb.connect(
            str(self.database_path),
            read_only=True,
        )

    def summary(self) -> dict:

        connection = self._connect()

        try:

            result = connection.execute(
                """
                SELECT

                    COUNT(*) AS invoice_count,

                    COALESCE(
                        SUM(total_amount),
                        0
                    ) AS total_spend,

                    COALESCE(
                        AVG(total_amount),
                        0
                    ) AS average_invoice,

                    COALESCE(
                        SUM(tax_amount),
                        0
                    ) AS total_tax

                FROM financial_documents
                """
            ).fetchone()

            return {
                "invoice_count": int(
                    result[0]
                ),
                "total_spend": float(
                    result[1]
                ),
                "average_invoice": float(
                    result[2]
                ),
                "total_tax": float(
                    result[3]
                ),
            }

        finally:

            connection.close()

    def vendor_spend(
        self,
    ) -> pd.DataFrame:

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT

                    vendor_name,

                    COUNT(*) AS invoice_count,

                    SUM(total_amount)
                        AS total_spend,

                    AVG(total_amount)
                        AS average_invoice

                FROM financial_documents

                GROUP BY vendor_name

                ORDER BY total_spend DESC
                """
            ).fetchdf()

        finally:

            connection.close()

    def category_spend(
        self,
    ) -> pd.DataFrame:

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT

                    COALESCE(
                        category,
                        'Uncategorized'
                    ) AS category,

                    SUM(total_price)
                        AS total_spend,

                    SUM(quantity)
                        AS total_quantity,

                    AVG(unit_price)
                        AS average_unit_price

                FROM line_items

                GROUP BY category

                ORDER BY total_spend DESC
                """
            ).fetchdf()

        finally:

            connection.close()

    def monthly_spend(
        self,
    ) -> pd.DataFrame:

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT

                    DATE_TRUNC(
                        'month',
                        invoice_date
                    ) AS month,

                    COUNT(*) AS invoice_count,

                    SUM(total_amount)
                        AS total_spend

                FROM financial_documents

                WHERE invoice_date IS NOT NULL

                GROUP BY month

                ORDER BY month
                """
            ).fetchdf()

        finally:

            connection.close()

    def tax_analysis(
        self,
    ) -> pd.DataFrame:

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT

                    currency,

                    COUNT(*) AS invoice_count,

                    SUM(subtotal)
                        AS subtotal,

                    SUM(tax_amount)
                        AS tax_amount,

                    SUM(total_amount)
                        AS total_amount

                FROM financial_documents

                GROUP BY currency

                ORDER BY total_amount DESC
                """
            ).fetchdf()

        finally:

            connection.close()

    def high_value_invoices(
        self,
        limit: int = 10,
    ) -> pd.DataFrame:

        if limit <= 0:

            raise ValueError(
                "limit must be greater than zero"
            )

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT

                    document_id,

                    vendor_name,

                    invoice_number,

                    invoice_date,

                    currency,

                    total_amount,

                    extraction_confidence

                FROM financial_documents

                ORDER BY total_amount DESC

                LIMIT ?
                """,
                [limit],
            ).fetchdf()

        finally:

            connection.close()