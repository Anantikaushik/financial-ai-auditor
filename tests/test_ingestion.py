from pathlib import Path

import pytest

from backend.ingestion.file_handler import (
    validate_file,
)


def test_valid_pdf():

    sample = Path(
        "data/sample/test_invoice.pdf"
    )

    if not sample.exists():
        pytest.skip(
            "Sample invoice not available"
        )

    result = validate_file(sample)

    assert result.exists()

    assert result.suffix.lower() == ".pdf"


def test_missing_file():

    with pytest.raises(
        FileNotFoundError
    ):

        validate_file(
            "data/sample/does_not_exist.pdf"
        )


def test_unsupported_extension(
    tmp_path
):

    file_path = (
        tmp_path / "test.txt"
    )

    file_path.write_text(
        "test"
    )

    with pytest.raises(
        ValueError,
        match="Unsupported file type",
    ):

        validate_file(file_path)