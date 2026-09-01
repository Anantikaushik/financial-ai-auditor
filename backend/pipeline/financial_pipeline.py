from pathlib import Path

from backend.database.duckdb_manager import DuckDBManager
from backend.ingestion.docling_parser import DoclingParser
from backend.schemas.financial import FinancialDocument
from backend.vision.extractor import FinancialExtractor
from backend.analysis.financial_analyzer import FinancialAnalyzer


class FinancialPipeline:

    def __init__(
        self,
        parser: DoclingParser | None = None,
        extractor: FinancialExtractor | None = None,
        database: DuckDBManager | None = None,
        vlm_client=None,
        analyzer: FinancialAnalyzer | None = None,
    ):

        self.parser = (
            parser or DoclingParser()
        )

        self.extractor = extractor

        self.vlm_client = vlm_client

        self.database = database

        self.analyzer = (
            analyzer
            or FinancialAnalyzer()
        )

        self.last_document = None

        self.last_audit = None

    def process(
        self,
        pdf_path: str | Path,
        image_path=None,
    ) -> FinancialDocument:

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():

            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        # -----------------------------------------
        # DOCLING
        # -----------------------------------------

        parsed = self.parser.parse(
            pdf_path
        )

        # -----------------------------------------
        # Convert Docling document to Markdown
        # -----------------------------------------

        try:

            document_text = (
                parsed.export_to_markdown()
            )

        except AttributeError:

            document_text = str(
                parsed
            )

        # -----------------------------------------
        # VLM extraction
        # -----------------------------------------

        if self.extractor is None:

            raise RuntimeError(
                "FinancialExtractor is not configured."
            )

        document = (
            self.extractor.extract(
                document_text=document_text,
                source_file=str(pdf_path),
                image_path=None,
            )
        )

        self.last_document = document

        # -----------------------------------------
        # FINANCIAL AUDIT
        # -----------------------------------------

        self.last_audit = (
            self.analyzer.analyze(
                document
            )
        )

        # -----------------------------------------
        # DATABASE
        # -----------------------------------------

        if self.database is not None:

            self.database.insert_document(
                document
            )

        return document