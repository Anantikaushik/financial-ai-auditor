from pathlib import Path

import pytest

from backend.ingestion.docling_parser import (
    DoclingParser,
)


def test_docling_to_markdown():

    sample = Path(
        "data/sample/test_invoice.pdf"
    )

    if not sample.exists():
        pytest.skip(
            "Sample invoice not available"
        )

    parser = DoclingParser()

    markdown = parser.to_markdown(
        sample
    )

    assert isinstance(
        markdown,
        str
    )

    assert len(markdown.strip()) > 0