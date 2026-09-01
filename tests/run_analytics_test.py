from backend.analytics.financial_analytics import (
    FinancialAnalytics,
)

from backend.config import settings


def main():

    analytics = FinancialAnalytics(
        settings.DATABASE_PATH
    )

    print("\n")
    print("=" * 70)
    print("FINANCIAL ANALYTICS")
    print("=" * 70)

    print("\nSUMMARY")
    print("-" * 70)

    print(
        analytics.summary()
    )

    print("\nVENDOR SPEND")
    print("-" * 70)

    print(
        analytics
        .vendor_spend()
        .to_string(index=False)
    )

    print("\nCATEGORY SPEND")
    print("-" * 70)

    print(
        analytics
        .category_spend()
        .to_string(index=False)
    )

    print("\nMONTHLY SPEND")
    print("-" * 70)

    print(
        analytics
        .monthly_spend()
        .to_string(index=False)
    )

    print("\nTAX ANALYSIS")
    print("-" * 70)

    print(
        analytics
        .tax_analysis()
        .to_string(index=False)
    )

    print("\nTOP INVOICES")
    print("-" * 70)

    print(
        analytics
        .high_value_invoices()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()