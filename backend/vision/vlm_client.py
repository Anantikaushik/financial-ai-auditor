import base64
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from groq import Groq

from backend.config import settings


# ============================================================
# VLM INTERFACE
# ============================================================

class VLMClient(ABC):

    @abstractmethod
    def extract(
        self,
        document_text: str,
        image_path=None,
    ) -> dict[str, Any]:
        """
        Extract structured financial information.
        """
        raise NotImplementedError


# ============================================================
# MOCK VLM
# ============================================================

class MockVLMClient(VLMClient):

    def extract(
        self,
        document_text: str,
        image_path=None,
    ) -> dict[str, Any]:

        return {
            "document_type": "invoice",

            "vendor_name": "Demo Supplier",

            "invoice_number": "INV-001",

            "invoice_date": "2026-08-20",

            "currency": "INR",

            "subtotal": 10000,

            "tax_amount": 1800,

            "total_amount": 11800,

            "payment_terms": "Net 30",

            "line_items": [
                {
                    "description": "Laptop",
                    "quantity": 1,
                    "unit_price": 10000,
                    "total_price": 10000,
                    "category": "Technology",
                }
            ],

            "extraction_confidence": 0.95,
        }


# ============================================================
# GROQ VLM
# ============================================================

class GroqVLMClient(VLMClient):
    """
    Groq-based financial document extraction client.

    Design goals:

    1. Fast text-first extraction.
    2. Avoid huge multimodal requests.
    3. Keep input below Groq TPM limits.
    4. Return valid JSON.
    5. Normalize invoice dates.
    6. Extract all available financial fields.
    """

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    #
    # Your Groq organization previously had:
    #
    # TPM LIMIT = 8000
    #
    # The previous request attempted ~44,923 tokens.
    #
    # Therefore we intentionally keep the document text
    # relatively small.
    #

    MAX_TEXT_CHARS = 14000

    MAX_COMPLETION_TOKENS = 1200

    # --------------------------------------------------------
    # Constructor
    # --------------------------------------------------------

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):

        self.api_key = (
            api_key
            or settings.VLM_API_KEY
        )

        self.model = (
            model
            or settings.VLM_MODEL
        )

        if not self.api_key:

            raise ValueError(
                "Groq API key is not configured."
            )

        self.client = Groq(
            api_key=self.api_key
        )

    # ========================================================
    # IMAGE HELPERS
    # ========================================================

    @staticmethod
    def _normalize_image_paths(
        image_path,
    ) -> list[Path]:

        if image_path is None:
            return []

        if isinstance(
            image_path,
            (str, Path),
        ):

            return [
                Path(image_path)
            ]

        if isinstance(
            image_path,
            (list, tuple),
        ):

            return [
                Path(path)
                for path in image_path
            ]

        raise TypeError(
            "image_path must be a path, "
            "Path, list of paths, or None."
        )

    @staticmethod
    def _encode_image(
        image_path: str | Path,
    ) -> str:

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if not image_path.is_file():

            raise FileNotFoundError(
                f"Image path is not a file: "
                f"{image_path}"
            )

        return base64.b64encode(
            image_path.read_bytes()
        ).decode("utf-8")

    # ========================================================
    # TEXT MANAGEMENT
    # ========================================================

    @staticmethod
    def _trim_text(
        text: str,
        max_chars: int,
    ) -> str:

        if not text:
            return ""

        text = str(text)

        if len(text) <= max_chars:
            return text

        # Keep beginning and end.
        #
        # Beginning:
        # vendor / invoice number / date
        #
        # End:
        # subtotal / tax / total
        #

        half = max_chars // 2

        return (
            text[:half]

            + "\n\n"
            + "[MIDDLE OF DOCUMENT OMITTED FOR TOKEN CONTROL]"
            + "\n\n"

            + text[-half:]
        )

    # ========================================================
    # PROMPT
    # ========================================================

    def _build_prompt(
        self,
        document_text: str,
    ) -> str:

        return f"""
You are a financial document extraction engine.

Your job is to extract financial information from
an invoice, receipt, purchase document, or similar
financial document.

Analyze the supplied document carefully.

Return EXACTLY ONE valid JSON object.

Do NOT return:

- Markdown
- ```json
- explanations
- comments
- analysis
- multiple JSON objects

==================================================
OUTPUT FORMAT
==================================================

{{
  "document_type": "invoice",
  "vendor_name": null,
  "invoice_number": null,
  "invoice_date": null,
  "currency": "INR",
  "subtotal": null,
  "tax_amount": null,
  "total_amount": null,
  "payment_terms": null,
  "line_items": [],
  "extraction_confidence": 0.0
}}

==================================================
LINE ITEM FORMAT
==================================================

Each line item MUST be:

{{
  "description": "",
  "quantity": 0,
  "unit_price": 0,
  "total_price": 0,
  "category": null
}}

==================================================
EXTRACTION RULES
==================================================

1. Extract only information actually present.

2. Never invent or guess values.

3. Use null when a value cannot be determined.

4. Numbers MUST be JSON numbers.

5. Do not include currency symbols inside numbers.

6. Preserve monetary values accurately.

7. Extract ALL identifiable line items.

8. Do not duplicate line items.

9. Preserve the product/item description.

10. Preserve invoice number exactly.

11. Preserve vendor name exactly.

12. Determine the correct currency from the document.

13. Extract subtotal when present.

14. Extract tax amount when present.

15. Extract total amount when present.

16. Extract payment terms when present.

==================================================
DATE RULE
==================================================

The invoice_date MUST ALWAYS be returned as:

YYYY-MM-DD

Examples:

23.05.2021
must become:
2021-05-23

23/05/2021
must become:
2021-05-23

23-05-2021
must become:
2021-05-23

2021/05/23
must become:
2021-05-23

2021.05.23
must become:
2021-05-23

If the date is unavailable:

"invoice_date": null

==================================================
FINANCIAL CALCULATION AWARENESS
==================================================

Do not modify values simply to make calculations match.

Extract the values exactly as printed.

For example:

subtotal = 5964.50
tax = 596.45
total = 6610.95

Return those exact values even if the
audit engine later detects an inconsistency.

==================================================
CONFIDENCE
==================================================

extraction_confidence must be a number between 0 and 1.

Use a high value when the document information
is clear.

Use a lower value when information is difficult
to read or ambiguous.

==================================================
DOCUMENT
==================================================

{document_text}

==================================================
FINAL REQUIREMENT
==================================================

Return ONLY the JSON object.
"""

    # ========================================================
    # GROQ REQUEST
    # ========================================================

    def _call_groq(
        self,
        prompt: str,
        image_paths: list[Path] | None = None,
    ) -> dict[str, Any]:

        content = [
            {
                "type": "text",
                "text": prompt,
            }
        ]

        # ----------------------------------------------------
        # OPTIONAL VISION MODE
        # ----------------------------------------------------
        #
        # We deliberately do NOT send images during normal
        # processing because the text-first pipeline is much
        # faster and avoids huge TPM usage.
        #
        # If images are explicitly supplied, only send a
        # maximum of ONE image.
        #

        if image_paths:

            first_image = image_paths[0]

            encoded = self._encode_image(
                first_image
            )

            content.append(
                {
                    "type": "text",
                    "text": (
                        "Use this document page image "
                        "as additional visual evidence."
                    ),
                }
            )

            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            "data:image/png;base64,"
                            + encoded
                        )
                    },
                }
            )

        # ----------------------------------------------------
        # API CALL
        # ----------------------------------------------------

        response = (
            self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],

                temperature=0,

                max_completion_tokens=(
                    self.MAX_COMPLETION_TOKENS
                ),

                reasoning_effort="none",

                response_format={
                    "type": "json_object"
                },
            )
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        response_text = (
            response
            .choices[0]
            .message
            .content
        )

        if not response_text:

            raise ValueError(
                "Groq returned an empty response."
            )

        response_text = response_text.strip()

        # ----------------------------------------------------
        # JSON PARSING
        # ----------------------------------------------------

        try:

            result = json.loads(
                response_text
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Groq returned invalid JSON.\n\n"
                f"Response:\n{response_text}"
            ) from exc

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                "Groq response must be a JSON object."
            )

        return result

    # ========================================================
    # MAIN EXTRACTION
    # ========================================================

    def extract(
        self,
        document_text: str,
        image_path=None,
    ) -> dict[str, Any]:

        # ----------------------------------------------------
        # Normalize text
        # ----------------------------------------------------

        if document_text is None:

            document_text = ""

        document_text = str(
            document_text
        ).strip()

        # ----------------------------------------------------
        # Prevent huge requests
        # ----------------------------------------------------

        document_text = self._trim_text(
            document_text,
            self.MAX_TEXT_CHARS,
        )

        # ----------------------------------------------------
        # FAST TEXT-FIRST MODE
        # ----------------------------------------------------
        #
        # We intentionally don't send all PDF pages.
        #
        # This prevents:
        #
        # 413 Request Too Large
        #
        # and dramatically reduces latency.
        #

        return self._call_groq(
            prompt=self._build_prompt(
                document_text
            ),

            image_paths=None,
        )