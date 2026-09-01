from decimal import Decimal

from backend.schemas.financial import (
    FinancialDocument,
    LineItem,
)


def test_line_item():

    item = LineItem(
        description="Laptop",
        quantity=2,
        unit_price=Decimal("50000"),
        total_price=Decimal("100000"),
        category="Technology",
    )

    assert item.description == "Laptop"

    assert item.quantity == 2

    assert item.unit_price == Decimal(
        "50000"
    )


def test_financial_document():

    document = FinancialDocument(
        document_id="TEST-001",
        vendor_name="ABC Ltd",
        invoice_number="INV-001",
        currency="INR",
        total_amount=Decimal("118000"),
        source_file="invoice.pdf",
    )

    assert document.vendor_name == "ABC Ltd"

    assert document.total_amount == Decimal(
        "118000"
    )