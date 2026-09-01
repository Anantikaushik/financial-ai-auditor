from pathlib import Path
from uuid import uuid4

from backend.schemas.financial import (
    FinancialDocument,
)

from backend.vision.vlm_client import (
    VLMClient,
)


class FinancialExtractor:
    """
    Converts raw VLM output into a validated
    FinancialDocument.
    """

    def __init__(
        self,
        vlm_client: VLMClient,
    ):
        self.vlm_client = vlm_client

    def extract(
        self,
        document_text: str,
        source_file: str,
        image_path= None,
    ) -> FinancialDocument:

        # -----------------------------------------------
        # Normalize image paths
        # -----------------------------------------------

        if image_path is None:

            image_paths = []

        elif isinstance(
            image_path,
            (str, Path),
        ):

            image_paths = [
                Path(image_path)
            ]

        elif isinstance(
            image_path,
            (list, tuple),
        ):

            image_paths = [
                Path(path)
                for path in image_path
            ]

        else:

            raise TypeError(
                "image_path must be a path, "
                "list of paths, or None."
            )

        # -----------------------------------------------
        # Verify paths before VLM call
        # -----------------------------------------------

        for path in image_paths:

            if not path.exists():

                raise FileNotFoundError(
                    f"Image not found: {path}"
                )

        # -----------------------------------------------
        # Call VLM
        # -----------------------------------------------

        raw_data = (
            self.vlm_client.extract(
                document_text=document_text,
                image_path=image_paths,
            )
        )

        # -----------------------------------------------
        # Add application metadata
        # -----------------------------------------------

        raw_data["document_id"] = str(
            uuid4()
        )

        raw_data["source_file"] = (
            source_file
        )

        # -----------------------------------------------
        # Validate with Pydantic
        # -----------------------------------------------

        return (
            FinancialDocument.model_validate(
                raw_data
            )
        )