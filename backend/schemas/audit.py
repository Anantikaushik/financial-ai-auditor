from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AuditFinding(BaseModel):
    """One financial audit finding."""

    severity: str
    category: str
    title: str
    message: str
    expected_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    difference: Optional[Decimal] = None


class AuditResult(BaseModel):
    """Result of deterministic financial analysis."""

    risk_score: float = Field(
        ge=0,
        le=100,
    )

    risk_level: str

    findings: list[AuditFinding] = Field(
        default_factory=list
    )

    checks_performed: int = 0

    checks_passed: int = 0

    checks_failed: int = 0

    summary: str = ""