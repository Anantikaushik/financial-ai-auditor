from decimal import Decimal

from backend.schemas.financial import FinancialDocument
from backend.schemas.audit import (
    AuditFinding,
    AuditResult,
)


class FinancialAnalyzer:
    """
    Deterministic financial audit engine.

    The VLM extracts financial information.
    This class independently validates the
    extracted information.

    Important distinction:
        - Confirmed financial anomalies
        - Possible extraction incompleteness
    """

    TOLERANCE = Decimal("0.01")

    def analyze(
        self,
        document: FinancialDocument,
    ) -> AuditResult:

        findings: list[AuditFinding] = []

        checks_performed = 0
        checks_passed = 0

        # ==================================================
        # CHECK 1 — Required invoice information
        # ==================================================

        required_fields = {
            "vendor_name": document.vendor_name,
            "invoice_number": document.invoice_number,
            "invoice_date": document.invoice_date,
        }

        for field, value in required_fields.items():

            checks_performed += 1

            if value is None or str(value).strip() == "":
                findings.append(
                    AuditFinding(
                        severity="MEDIUM",
                        category="Missing Information",
                        title=(
                            f"Missing "
                            f"{field.replace('_', ' ').title()}"
                        ),
                        message=(
                            f"The document does not contain a "
                            f"reliable {field.replace('_', ' ')}."
                        ),
                    )
                )
            else:
                checks_passed += 1

        # ==================================================
        # CHECK 2 — Line item calculations
        # ==================================================

        calculated_subtotal = Decimal("0")

        line_item_errors = 0

        for index, item in enumerate(
            document.line_items,
            start=1,
        ):

            checks_performed += 1

            expected_total = (
                Decimal(str(item.quantity))
                * item.unit_price
            )

            if item.total_price is not None:

                difference = (
                    item.total_price
                    - expected_total
                )

                if abs(difference) > self.TOLERANCE:

                    line_item_errors += 1

                    findings.append(
                        AuditFinding(
                            severity="HIGH",
                            category="Calculation Error",
                            title=(
                                f"Line Item {index} "
                                "Calculation Mismatch"
                            ),
                            message=(
                                f"{item.description}: "
                                "quantity × unit price does not "
                                "match the reported line total."
                            ),
                            expected_value=expected_total,
                            actual_value=item.total_price,
                            difference=difference,
                        )
                    )

                else:
                    checks_passed += 1

            else:
                # No reported line total.
                # Use quantity × unit price for reconciliation.
                checks_passed += 1

            calculated_subtotal += (
                item.total_price
                if item.total_price is not None
                else expected_total
            )

        # ==================================================
        # CHECK 3 — Subtotal reconciliation
        # ==================================================
        #
        # IMPORTANT:
        #
        # We do NOT automatically classify a subtotal
        # mismatch as a financial anomaly.
        #
        # If the VLM extracted only part of the invoice,
        # the calculated line-item subtotal will naturally
        # be lower than the declared subtotal.
        #
        # Therefore this is treated as an
        # "Extraction Completeness" warning.
        # ==================================================

        if (
            document.subtotal is not None
            and document.line_items
        ):

            checks_performed += 1

            difference = (
                document.subtotal
                - calculated_subtotal
            )

            if abs(difference) <= self.TOLERANCE:

                checks_passed += 1

            else:

                findings.append(
                    AuditFinding(
                        severity="LOW",
                        category="Extraction Completeness",
                        title=(
                            "Line-Item Reconciliation "
                            "Requires Verification"
                        ),
                        message=(
                            "The extracted line items do not "
                            "fully reconcile with the declared "
                            "subtotal. This may indicate that "
                            "some line items were not extracted. "
                            "This is treated as an extraction "
                            "warning rather than a confirmed "
                            "financial anomaly."
                        ),
                        expected_value=calculated_subtotal,
                        actual_value=document.subtotal,
                        difference=difference,
                    )
                )

        # ==================================================
        # CHECK 4 — Tax + subtotal = total
        # ==================================================

        if (
            document.subtotal is not None
            and document.tax_amount is not None
            and document.total_amount is not None
        ):

            checks_performed += 1

            expected_total = (
                document.subtotal
                + document.tax_amount
            )

            difference = (
                document.total_amount
                - expected_total
            )

            if abs(difference) > self.TOLERANCE:

                findings.append(
                    AuditFinding(
                        severity="HIGH",
                        category="Total Mismatch",
                        title="Total Amount Is Inconsistent",
                        message=(
                            "Subtotal plus tax does not "
                            "match the reported total. "
                            "This is a confirmed arithmetic "
                            "inconsistency in the extracted "
                            "financial values."
                        ),
                        expected_value=expected_total,
                        actual_value=document.total_amount,
                        difference=difference,
                    )
                )

            else:
                checks_passed += 1

        # ==================================================
        # CHECK 5 — Tax sanity
        # ==================================================

        if (
            document.subtotal is not None
            and document.tax_amount is not None
        ):

            checks_performed += 1

            if document.subtotal == 0:

                findings.append(
                    AuditFinding(
                        severity="HIGH",
                        category="Tax Validation",
                        title="Invalid Tax Base",
                        message=(
                            "Tax is present while the "
                            "subtotal is zero."
                        ),
                        actual_value=document.tax_amount,
                    )
                )

            elif document.tax_amount < 0:

                findings.append(
                    AuditFinding(
                        severity="HIGH",
                        category="Tax Validation",
                        title="Negative Tax Amount",
                        message=(
                            "The extracted tax amount "
                            "is negative."
                        ),
                        actual_value=document.tax_amount,
                    )
                )

            else:
                checks_passed += 1

        # ==================================================
        # CHECK 6 — Total sanity
        # ==================================================

        if document.total_amount is not None:

            checks_performed += 1

            if document.total_amount <= 0:

                findings.append(
                    AuditFinding(
                        severity="HIGH",
                        category="Amount Validation",
                        title="Invalid Total Amount",
                        message=(
                            "The document total is "
                            "zero or negative."
                        ),
                        actual_value=document.total_amount,
                    )
                )

            else:
                checks_passed += 1

        # ==================================================
        # CHECK 7 — Extraction confidence
        # ==================================================

        if document.extraction_confidence is not None:

            checks_performed += 1

            if document.extraction_confidence < 0.60:

                findings.append(
                    AuditFinding(
                        severity="MEDIUM",
                        category="Extraction Quality",
                        title="Low Extraction Confidence",
                        message=(
                            "The VLM reported low confidence "
                            "in the extracted information."
                        ),
                    )
                )

            else:
                checks_passed += 1

        # ==================================================
        # RISK SCORE
        # ==================================================

        risk_score = self._calculate_risk_score(
            findings
        )

        risk_level = self._risk_level(
            risk_score
        )

        checks_failed = (
            checks_performed
            - checks_passed
        )

        # ==================================================
        # SUMMARY
        # ==================================================

        confirmed_findings = [
            finding
            for finding in findings
            if finding.category
            not in {
                "Extraction Completeness",
                "Extraction Quality",
            }
        ]

        extraction_warnings = [
            finding
            for finding in findings
            if finding.category
            in {
                "Extraction Completeness",
                "Extraction Quality",
            }
        ]

        if confirmed_findings:

            summary = (
                f"Automated audit identified "
                f"{len(confirmed_findings)} confirmed "
                f"financial finding(s). "
                f"Overall risk level: {risk_level}."
            )

        elif extraction_warnings:

            summary = (
                "No confirmed financial inconsistencies "
                "were detected. However, the extracted "
                "document requires completeness verification."
            )

        else:

            summary = (
                "No financial inconsistencies were "
                "detected by the automated audit checks."
            )

        return AuditResult(
            risk_score=risk_score,
            risk_level=risk_level,
            findings=findings,
            checks_performed=checks_performed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            summary=summary,
        )

    # ======================================================
    # RISK CALCULATION
    # ======================================================

    @staticmethod
    def _calculate_risk_score(
        findings: list[AuditFinding],
    ) -> float:

        score = 0

        weights = {
            "HIGH": 30,
            "MEDIUM": 15,
            "LOW": 0,
        }

        for finding in findings:

            score += weights.get(
                finding.severity.upper(),
                0,
            )

        return float(
            min(score, 100)
        )

    # ======================================================
    # RISK LEVEL
    # ======================================================

    @staticmethod
    def _risk_level(
        score: float,
    ) -> str:

        if score >= 70:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        return "LOW"