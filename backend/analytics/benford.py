from collections import Counter
from decimal import Decimal
from typing import Iterable


# Benford's Law expected probabilities
BENFORD_EXPECTED = {
    1: 0.301,
    2: 0.176,
    3: 0.125,
    4: 0.097,
    5: 0.079,
    6: 0.067,
    7: 0.058,
    8: 0.051,
    9: 0.046,
}


def first_digit(
    value: float | int | Decimal,
) -> int | None:
    """
    Return the first significant digit
    of a positive number.
    """

    value = abs(float(value))

    if value == 0:
        return None

    text = f"{value:.15g}"

    for character in text:

        if character.isdigit() and character != "0":

            return int(character)

    return None


def extract_first_digits(
    values: Iterable[
        float | int | Decimal
    ],
) -> list[int]:

    digits = []

    for value in values:

        digit = first_digit(value)

        if digit is not None:

            digits.append(digit)

    return digits


def calculate_digit_distribution(
    values: Iterable[
        float | int | Decimal
    ],
) -> dict[int, float]:

    digits = extract_first_digits(
        values
    )

    if not digits:
        return {}

    counts = Counter(digits)

    total = len(digits)

    return {
        digit: counts.get(digit, 0) / total
        for digit in range(1, 10)
    }


def calculate_benford_deviation(
    values: Iterable[
        float | int | Decimal
    ],
) -> float:

    observed = calculate_digit_distribution(
        values
    )

    if not observed:
        return 0.0

    deviation = 0.0

    for digit in range(1, 10):

        expected = BENFORD_EXPECTED[
            digit
        ]

        actual = observed.get(
            digit,
            0.0,
        )

        deviation += abs(
            actual - expected
        )

    return deviation / 2


def benford_analysis(
    values: Iterable[
        float | int | Decimal
    ],
) -> dict:

    values = list(values)

    digits = extract_first_digits(
        values
    )

    distribution = (
        calculate_digit_distribution(
            values
        )
    )

    deviation = (
        calculate_benford_deviation(
            values
        )
    )

    return {
        "sample_size": len(values),

        "valid_values": len(digits),

        "distribution": distribution,

        "expected_distribution":
            BENFORD_EXPECTED.copy(),

        "deviation": deviation,
    }