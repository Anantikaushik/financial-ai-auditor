from pathlib import Path

import pytest

from backend.ingestion.document_renderer import (
    DocumentRenderer,
)


def test_pdf_rendering(
    tmp_path,
):

    pdf_path = Path(
        "data/sample/test_invoice.pdf"
    )

    if not pdf_path.exists():
        pytest.skip(
            "Sample invoice PDF not available"
        )

    output_dir = (
        tmp_path / "rendered"
    )

    renderer = DocumentRenderer(
        dpi=150
    )

    pages = renderer.render_pdf(
        pdf_path,
        output_dir,
    )

    assert len(pages) > 0

    for page in pages:

        assert page.exists()

        assert page.suffix.lower() == ".png"