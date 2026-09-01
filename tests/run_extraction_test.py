from backend.vision.extractor import (
    FinancialExtractor,
)

from backend.vision.vlm_client import (
    MockVLMClient,
)


def main():

    client = MockVLMClient()

    extractor = FinancialExtractor(
        client
    )

    document = extractor.extract(
        document_text="""
        Demo invoice.

        Vendor: Demo Supplier
        Invoice: INV-001
        Total: INR 11800
        """,
        source_file="demo_invoice.pdf",
    )

    print("\nEXTRACTION RESULT")
    print("=" * 50)

    print(
        document.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()