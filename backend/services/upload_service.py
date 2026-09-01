from pathlib import Path
from uuid import uuid4

from backend.config import settings
from backend.pipeline.financial_pipeline import FinancialPipeline
from backend.vision.vlm_client import GroqVLMClient
from backend.vision.extractor import FinancialExtractor


class UploadService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
    }

    def __init__(self):

        # -----------------------------------------
        # Groq VLM
        # -----------------------------------------

        vlm_client = GroqVLMClient()

        # -----------------------------------------
        # Financial extractor
        # -----------------------------------------

        extractor = FinancialExtractor(
            vlm_client=vlm_client
        )

        # -----------------------------------------
        # Financial pipeline
        # -----------------------------------------

        self.pipeline = FinancialPipeline(
            extractor=extractor,
            vlm_client=vlm_client,
        )

    def validate_file(
        self,
        file_name: str,
        file_size: int,
    ) -> None:

        extension = Path(
            file_name
        ).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:

            raise ValueError(
                "Unsupported file type. "
                "Upload PDF, PNG, JPG or JPEG."
            )

        max_size = (
            settings.MAX_FILE_SIZE_MB
            * 1024
            * 1024
        )

        if file_size > max_size:

            raise ValueError(
                f"File is too large. "
                f"Maximum size is "
                f"{settings.MAX_FILE_SIZE_MB} MB."
            )

    def save_upload(
        self,
        file_bytes: bytes,
        file_name: str,
    ) -> Path:

        raw_dir = Path(
            settings.RAW_DATA_DIR
        )

        raw_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = Path(
            file_name
        ).suffix.lower()

        safe_name = (
            f"{uuid4().hex}{extension}"
        )

        output_path = (
            raw_dir / safe_name
        )

        output_path.write_bytes(
            file_bytes
        )

        return output_path

    def process(
        self,
        file_bytes: bytes,
        file_name: str,
    ):

        self.validate_file(
            file_name=file_name,
            file_size=len(file_bytes),
        )

        saved_path = self.save_upload(
            file_bytes=file_bytes,
            file_name=file_name,
        )

        result = self.pipeline.process(
            pdf_path=saved_path,
        )

        return {
            "document": result,
            "audit": self.pipeline.last_audit,
        }