from backend.anomaly.risk_engine import (
    RiskEngine,
)


def test_low_risk():

    engine = RiskEngine()

    result = engine.assess(
        benford_score=0.10,
        anomaly_score=0.10,
        duplicate_score=0.0,
    )

    assert result.risk_level == "LOW"


def test_high_risk():

    engine = RiskEngine()

    result = engine.assess(
        benford_score=0.90,
        anomaly_score=0.90,
        duplicate_score=1.0,
    )

    assert result.risk_level == "HIGH"


def test_duplicate_increases_risk():

    engine = RiskEngine()

    without_duplicate = engine.assess(
        benford_score=0.2,
        anomaly_score=0.3,
        duplicate_score=0.0,
    )

    with_duplicate = engine.assess(
        benford_score=0.2,
        anomaly_score=0.3,
        duplicate_score=1.0,
    )

    assert (
        with_duplicate.final_score
        > without_duplicate.final_score
    )


def test_score_range():

    engine = RiskEngine()

    result = engine.assess(
        benford_score=0.5,
        anomaly_score=0.6,
        duplicate_score=0.5,
    )

    assert 0 <= result.final_score <= 1