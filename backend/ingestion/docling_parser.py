from pathlib import Path

from docling.document_converter import DocumentConverter


class DoclingParser:
    """
    Handles document conversion using Docling.
    """

    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, file_path: str | Path):
        """
        Convert a document into a Docling document object.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        result = self.converter.convert(
            source=file_path
        )

        return result.document

    def to_markdown(
        self,
        file_path: str | Path
    ) -> str:
        """
        Convert a document directly to Markdown.
        """

        document = self.parse(file_path)

        return document.export_to_markdown()

    def save_markdown(
        self,
        file_path: str | Path,
        output_path: str | Path,
    ) -> Path:
        """
        Convert a document to Markdown and save it.
        """

        markdown = self.to_markdown(
            file_path
        )

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            markdown,
            encoding="utf-8"
        )

        return output_path