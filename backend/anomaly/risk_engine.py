from dataclasses import dataclass


@dataclass
class RiskAssessment:

    benford_score: float

    anomaly_score: float

    duplicate_score: float

    final_score: float

    risk_level: str


class RiskEngine:
    """
    Combines multiple financial anomaly signals.
    """

    def assess(
        self,
        benford_score: float,
        anomaly_score: float,
        duplicate_score: float = 0.0,
    ) -> RiskAssessment:

        benford_score = max(
            0.0,
            min(1.0, benford_score),
        )

        anomaly_score = max(
            0.0,
            min(1.0, anomaly_score),
        )

        duplicate_score = max(
            0.0,
            min(1.0, duplicate_score),
        )

        final_score = (
            0.25 * benford_score
            + 0.50 * anomaly_score
            + 0.25 * duplicate_score
        )

        if final_score >= 0.70:

            risk_level = "HIGH"

        elif final_score >= 0.40:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        return RiskAssessment(
            benford_score=benford_score,
            anomaly_score=anomaly_score,
            duplicate_score=duplicate_score,
            final_score=final_score,
            risk_level=risk_level,
        )