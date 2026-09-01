from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LineItem(BaseModel):
    """Represents one purchased item."""

    description: str = Field(
        min_length=1
    )

    quantity: float = Field(
        gt=0
    )

    unit_price: Decimal = Field(
        ge=0
    )

    total_price: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    category: Optional[str] = None

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: str
    ) -> str:

        return value.strip()


class FinancialDocument(BaseModel):
    """Canonical representation of a financial document."""

    document_id: str

    document_type: str = "invoice"

    vendor_name: Optional[str] = None

    invoice_number: Optional[str] = None

    invoice_date: Optional[date] = None

    currency: str = "INR"

    subtotal: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    tax_amount: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    total_amount: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    payment_terms: Optional[str] = None

    line_items: list[LineItem] = Field(
        default_factory=list
    )

    source_file: str

    extraction_confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1
    )

    # --------------------------------------------------
    # NORMALIZE INVOICE DATE
    # --------------------------------------------------

    @field_validator(
        "invoice_date",
        mode="before"
    )
    @classmethod
    def normalize_invoice_date(
        cls,
        value
    ):

        if value is None:
            return None

        if isinstance(value, date):
            return value

        if isinstance(value, datetime):
            return value.date()

        value = str(value).strip()

        if not value:
            return None

        # Common invoice date formats
        formats = [
            "%Y-%m-%d",   # 2021-05-23
            "%d.%m.%Y",   # 23.05.2021
            "%d-%m-%Y",   # 23-05-2021
            "%d/%m/%Y",   # 23/05/2021
            "%Y.%m.%d",   # 2021.05.23
            "%Y/%m/%d",   # 2021/05/23
            "%m/%d/%Y",   # 05/23/2021
            "%m-%d-%Y",   # 05-23-2021
            "%d.%m.%y",   # 23.05.21
            "%d/%m/%y",   # 23/05/21
            "%d-%m-%y",   # 23-05-21
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    value,
                    fmt
                ).date()

            except ValueError:
                continue

        raise ValueError(
            f"Unsupported invoice date format: {value}"
        )