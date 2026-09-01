from pathlib import Path

from backend.ingestion.docling_parser import (
    DoclingParser,
)


INPUT_FILE = Path(
    "data/sample/test_invoice.pdf"
)

OUTPUT_FILE = Path(
    "data/processed/test_invoice.md"
)


def main():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Missing: {INPUT_FILE}"
        )

    parser = DoclingParser()

    output = parser.save_markdown(
        INPUT_FILE,
        OUTPUT_FILE,
    )

    print(
        f"Markdown saved to: {output}"
    )


if __name__ == "__main__":
    main()