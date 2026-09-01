from backend.analytics.benford import (
    benford_analysis,
    first_digit,
)


def test_first_digit():

    assert first_digit(12345) == 1

    assert first_digit(9876) == 9

    assert first_digit(0) is None


def test_benford_analysis():

    values = [
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
    ]

    result = benford_analysis(
        values
    )

    assert (
        result["sample_size"]
        == 9
    )

    assert (
        result["valid_values"]
        == 9
    )

    assert (
        len(result["distribution"])
        == 9
    )


def test_empty_values():

    result = benford_analysis([])

    assert (
        result["sample_size"]
        == 0
    )

    assert (
        result["distribution"]
        == {}
    )