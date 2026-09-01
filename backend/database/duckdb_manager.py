from pathlib import Path

import duckdb

from backend.config import settings
from backend.schemas.financial import (
    FinancialDocument,
)


class DuckDBManager:
    """
    Handles persistent storage of financial
    documents and line items.
    """

    def __init__(
        self,
        database_path: str | None = None,
    ):

        self.database_path = Path(
            database_path
            or settings.DATABASE_PATH
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    def _connect(self):

        return duckdb.connect(
            str(self.database_path)
        )

    def initialize(self):

        connection = self._connect()

        try:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                financial_documents (

                    document_id VARCHAR PRIMARY KEY,

                    document_type VARCHAR,

                    vendor_name VARCHAR,

                    invoice_number VARCHAR,

                    invoice_date DATE,

                    currency VARCHAR,

                    subtotal DECIMAL(18, 2),

                    tax_amount DECIMAL(18, 2),

                    total_amount DECIMAL(18, 2),

                    payment_terms VARCHAR,

                    source_file VARCHAR,

                    extraction_confidence DOUBLE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                line_items (

                    line_item_id BIGINT
                    PRIMARY KEY,

                    document_id VARCHAR,

                    description VARCHAR,

                    quantity DOUBLE,

                    unit_price DECIMAL(18, 2),

                    total_price DECIMAL(18, 2),

                    category VARCHAR,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        finally:

            connection.close()

    def insert_document(
        self,
        document: FinancialDocument,
    ):

        connection = self._connect()

        try:

            connection.execute(
                """
                INSERT OR REPLACE INTO
                financial_documents (

                    document_id,
                    document_type,
                    vendor_name,
                    invoice_number,
                    invoice_date,
                    currency,
                    subtotal,
                    tax_amount,
                    total_amount,
                    payment_terms,
                    source_file,
                    extraction_confidence

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    document.document_id,
                    document.document_type,
                    document.vendor_name,
                    document.invoice_number,
                    document.invoice_date,
                    document.currency,
                    document.subtotal,
                    document.tax_amount,
                    document.total_amount,
                    document.payment_terms,
                    document.source_file,
                    document.extraction_confidence,
                ],
            )

            connection.execute(
                """
                DELETE FROM line_items
                WHERE document_id = ?
                """,
                [
                    document.document_id
                ],
            )

            for index, item in enumerate(
                document.line_items
            ):

                line_item_id = (
                    abs(
                        hash(
                            (
                                document.document_id,
                                index,
                            )
                        )
                    )
                    % 9223372036854775807
                )

                connection.execute(
                    """
                    INSERT INTO line_items (

                        line_item_id,
                        document_id,
                        description,
                        quantity,
                        unit_price,
                        total_price,
                        category

                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        line_item_id,
                        document.document_id,
                        item.description,
                        item.quantity,
                        item.unit_price,
                        item.total_price,
                        item.category,
                    ],
                )

        finally:

            connection.close()

    def get_documents(self):

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT *
                FROM financial_documents
                ORDER BY created_at DESC
                """
            ).fetchdf()

        finally:

            connection.close()

    def get_line_items(self):

        connection = self._connect()

        try:

            return connection.execute(
                """
                SELECT *
                FROM line_items
                ORDER BY created_at DESC
                """
            ).fetchdf()

        finally:

            connection.close()