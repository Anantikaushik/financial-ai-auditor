from backend.database.duckdb_manager import (
    DuckDBManager,
)


def main():

    database = DuckDBManager()

    print("\nFINANCIAL DOCUMENTS")
    print("=" * 60)

    documents = (
        database.get_documents()
    )

    print(documents.to_string(
        index=False
    ))

    print("\nLINE ITEMS")
    print("=" * 60)

    line_items = (
        database.get_line_items()
    )

    print(line_items.to_string(
        index=False
    ))


if __name__ == "__main__":
    main()