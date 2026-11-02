
import sqlite3
from pathlib import Path

import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "ecommerce.db"

# CSV files and their SQLite table names
FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}


def main():
    print("Starting database creation...")

    # Check that all CSV files exist
    for filename in FILES:
        if not (DATA_DIR / filename).exists():
            raise FileNotFoundError(
                f"Missing file: {DATA_DIR / filename}"
            )

    connection = sqlite3.connect(DB_PATH)

    try:
        for filename, table_name in FILES.items():
            file_path = DATA_DIR / filename

            print(f"\nLoading {filename}...")

            first_chunk = True
            total_rows = 0

            for chunk in pd.read_csv(
                file_path,
                chunksize=50000
            ):
                chunk.to_sql(
                    table_name,
                    connection,
                    if_exists="replace" if first_chunk else "append",
                    index=False
                )

                total_rows += len(chunk)
                first_chunk = False

            print(f"Created table: {table_name}")
            print(f"Rows imported: {total_rows:,}")

        print("\nDatabase created successfully!")
        print(f"Location: {DB_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
