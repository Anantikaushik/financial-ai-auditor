from pathlib import Path

from backend.database.duckdb_manager import (
    DuckDBManager,
)

from backend.pipeline.financial_pipeline import (
    FinancialPipeline,
)

from backend.vision.vlm_client import (
    GroqVLMClient,
)


PDF = Path(
    "data/sample/test_invoice.pdf"
)

IMAGE = Path(
    "data/processed/rendered/page_0001.png"
)


def main():

    if not PDF.exists():
        raise FileNotFoundError(
            f"Missing PDF: {PDF}"
        )

    if not IMAGE.exists():
        raise FileNotFoundError(
            f"Missing image: {IMAGE}"
        )

    vlm = GroqVLMClient()

    database = DuckDBManager()

    pipeline = FinancialPipeline(
        vlm_client=vlm,
        database=database,
    )

    document = pipeline.process(
        pdf_path=PDF,
        image_path=IMAGE,
    )

    print("\n")
    print("=" * 70)
    print("FINANCIAL AI AUDITOR")
    print("END-TO-END PIPELINE")
    print("=" * 70)

    print(
        document.model_dump_json(
            indent=2
        )
    )

    print("\nDATABASE RECORDS")
    print("=" * 70)

    print(
        database
        .get_documents()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()