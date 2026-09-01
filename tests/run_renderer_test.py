from pathlib import Path

from backend.ingestion.document_renderer import (
    DocumentRenderer,
)


INPUT_FILE = Path(
    "data/sample/test_invoice.pdf"
)

OUTPUT_DIR = Path(
    "data/processed/rendered"
)


def main():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Missing: {INPUT_FILE}"
        )

    renderer = DocumentRenderer(
        dpi=150
    )

    pages = renderer.render_pdf(
        INPUT_FILE,
        OUTPUT_DIR,
    )

    print(
        f"Rendered {len(pages)} page(s)"
    )

    for page in pages:

        print(page)


if __name__ == "__main__":
    main()