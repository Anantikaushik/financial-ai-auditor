from decimal import Decimal

from backend.analytics.financial_analytics import (
    FinancialAnalytics,
)

from backend.database.duckdb_manager import (
    DuckDBManager,
)

from backend.schemas.financial import (
    FinancialDocument,
    LineItem,
)


def create_test_database(
    tmp_path,
):

    database_path = (
        tmp_path / "analytics.duckdb"
    )

    database = DuckDBManager(
        database_path
    )

    documents = [

        FinancialDocument(

            document_id="DOC-001",

            document_type="invoice",

            vendor_name="Vendor A",

            invoice_number="INV-001",

            invoice_date="2026-08-01",

            currency="INR",

            subtotal=Decimal("10000"),

            tax_amount=Decimal("1800"),

            total_amount=Decimal("11800"),

            source_file="a.pdf",

            extraction_confidence=0.95,

            line_items=[

                LineItem(

                    description="Laptop",

                    quantity=1,

                    unit_price=Decimal(
                        "10000"
                    ),

                    total_price=Decimal(
                        "10000"
                    ),

                    category="Technology",
                )
            ],
        ),

        FinancialDocument(

            document_id="DOC-002",

            document_type="invoice",

            vendor_name="Vendor B",

            invoice_number="INV-002",

            invoice_date="2026-08-15",

            currency="INR",

            subtotal=Decimal("5000"),

            tax_amount=Decimal("900"),

            total_amount=Decimal("5900"),

            source_file="b.pdf",

            extraction_confidence=0.92,

            line_items=[

                LineItem(

                    description="Chair",

                    quantity=2,

                    unit_price=Decimal(
                        "2500"
                    ),

                    total_price=Decimal(
                        "5000"
                    ),

                    category="Furniture",
                )
            ],
        ),
    ]

    for document in documents:

        database.insert_document(
            document
        )

    return database_path


def test_summary(tmp_path):

    database_path = (
        create_test_database(
            tmp_path
        )
    )

    analytics = FinancialAnalytics(
        database_path
    )

    result = analytics.summary()

    assert (
        result["invoice_count"]
        == 2
    )

    assert (
        result["total_spend"]
        == 17700
    )

    assert (
        result["total_tax"]
        == 2700
    )


def test_vendor_spend(tmp_path):

    database_path = (
        create_test_database(
            tmp_path
        )
    )

    analytics = FinancialAnalytics(
        database_path
    )

    result = (
        analytics.vendor_spend()
    )

    assert len(result) == 2

    assert (
        result.iloc[0]["vendor_name"]
        == "Vendor A"
    )


def test_category_spend(tmp_path):

    database_path = (
        create_test_database(
            tmp_path
        )
    )

    analytics = FinancialAnalytics(
        database_path
    )

    result = (
        analytics.category_spend()
    )

    assert len(result) == 2

    assert set(
        result["category"]
    ) == {
        "Technology",
        "Furniture",
    }


def test_monthly_spend(tmp_path):

    database_path = (
        create_test_database(
            tmp_path
        )
    )

    analytics = FinancialAnalytics(
        database_path
    )

    result = (
        analytics.monthly_spend()
    )

    assert len(result) == 1

    assert (
        result.iloc[0]["total_spend"]
        == 17700
    )


def test_high_value_invoices(
    tmp_path,
):

    database_path = (
        create_test_database(
            tmp_path
        )
    )

    analytics = FinancialAnalytics(
        database_path
    )

    result = (
        analytics.high_value_invoices(
            limit=1
        )
    )

    assert len(result) == 1

    assert (
        result.iloc[0]["total_amount"]
        == 11800
    )