from decimal import Decimal

from backend.database.duckdb_manager import (
    DuckDBManager,
)

from backend.schemas.financial import (
    FinancialDocument,
    LineItem,
)


def test_database_insert_and_read(
    tmp_path,
):

    database_path = (
        tmp_path / "test.duckdb"
    )

    database = DuckDBManager(
        database_path
    )

    document = FinancialDocument(

        document_id="TEST-001",

        document_type="invoice",

        vendor_name="ABC Technologies",

        invoice_number="INV-001",

        currency="INR",

        subtotal=Decimal(
            "100000"
        ),

        tax_amount=Decimal(
            "18000"
        ),

        total_amount=Decimal(
            "118000"
        ),

        source_file="invoice.pdf",

        extraction_confidence=0.95,

        line_items=[

            LineItem(

                description="Laptop",

                quantity=2,

                unit_price=Decimal(
                    "50000"
                ),

                total_price=Decimal(
                    "100000"
                ),

                category="Technology",
            )
        ],
    )

    database.insert_document(
        document
    )

    documents = (
        database.get_documents()
    )

    line_items = (
        database.get_line_items()
    )

    assert len(documents) == 1

    assert (
        documents.iloc[0][
            "vendor_name"
        ]
        == "ABC Technologies"
    )

    assert (
        documents.iloc[0][
            "total_amount"
        ]
        == 118000
    )

    assert len(line_items) == 1

    assert (
        line_items.iloc[0][
            "description"
        ]
        == "Laptop"
    )
