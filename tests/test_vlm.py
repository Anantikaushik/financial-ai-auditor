from backend.vision.vlm_client import (
    MockVLMClient,
)

from backend.vision.extractor import (
    FinancialExtractor,
)


def test_mock_vlm():

    client = MockVLMClient()

    result = client.extract(
        document_text="Sample invoice"
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        "vendor_name"
    ] == "Demo Supplier"

    assert result[
        "total_amount"
    ] == 11800


def test_financial_extractor():

    client = MockVLMClient()

    extractor = FinancialExtractor(
        client
    )

    document = extractor.extract(
        document_text="Sample invoice",
        source_file="invoice.pdf",
    )

    assert (
        document.vendor_name
        == "Demo Supplier"
    )

    assert (
        document.total_amount
        == 11800
    )

    assert (
        document.document_id
    )

    assert (
        document.source_file
        == "invoice.pdf"
    )
    