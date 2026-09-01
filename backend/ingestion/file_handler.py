from pathlib import Path

from backend.config import settings


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".docx",
}


def validate_file(
    file_path: str | Path
) -> Path:
    """
    Validate that the uploaded document
    exists, is supported, and is within
    the configured size limit.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    max_bytes = (
        settings.MAX_FILE_SIZE_MB
        * 1024
        * 1024
    )

    if path.stat().st_size > max_bytes:
        raise ValueError(
            f"File exceeds "
            f"{settings.MAX_FILE_SIZE_MB} MB limit"
        )

    return path