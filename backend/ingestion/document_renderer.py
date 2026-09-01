from pathlib import Path

import fitz


class DocumentRenderer:
    """
    Converts PDF pages into images for
    multimodal/VLM processing.
    """

    def __init__(
        self,
        dpi: int = 150,
    ):
        self.dpi = dpi

    def render_pdf(
        self,
        pdf_path: str | Path,
        output_dir: str | Path,
    ) -> list[Path]:

        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                "DocumentRenderer currently "
                "supports PDF files only."
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = fitz.open(
            pdf_path
        )

        output_files = []

        zoom = self.dpi / 72

        matrix = fitz.Matrix(
            zoom,
            zoom,
        )

        try:

            for page_number, page in enumerate(
                document
            ):

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                output_path = (
                    output_dir
                    / f"page_{page_number + 1:04d}.png"
                )

                pixmap.save(
                    output_path
                )

                output_files.append(
                    output_path
                )

        finally:

            document.close()

        return output_files