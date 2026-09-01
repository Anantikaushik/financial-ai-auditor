from pathlib import Path

from backend.vision.extractor import (
    FinancialExtractor,
)

from backend.vision.vlm_client import (
    GroqVLMClient,
)


IMAGE = Path(
    "data/processed/rendered/page_0001.png"
)

MARKDOWN = Path(
    "data/processed/test_invoice.md"
)


def main():

    if not IMAGE.exists():
        raise FileNotFoundError(
            f"Missing image: {IMAGE}"
        )

    if not MARKDOWN.exists():
        raise FileNotFoundError(
            f"Missing markdown: {MARKDOWN}"
        )

    document_text = (
        MARKDOWN.read_text(
            encoding="utf-8"
        )
    )

    client = GroqVLMClient()

    extractor = FinancialExtractor(
        client
    )

    document = extractor.extract(
        document_text=document_text,
        source_file="test_invoice.pdf",
        image_path=str(IMAGE),
    )

    print("\n")
    print("=" * 60)
    print("FINANCIAL AI AUDITOR")
    print("GROQ + QWEN 3.6 VISION EXTRACTION")
    print("=" * 60)

    print(
        document.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()