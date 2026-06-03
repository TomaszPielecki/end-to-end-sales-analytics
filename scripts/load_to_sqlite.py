from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "sales_data.csv"
DB_PATH = BASE_DIR / "data" / "sales_analytics.db"
SCHEMA_PATH = BASE_DIR / "sql" / "01_create_schema.sql"


def load_sales_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["order_date"])


def create_database(connection: sqlite3.Connection) -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema_sql)


def load_dimensions_and_fact(connection: sqlite3.Connection, sales: pd.DataFrame) -> None:
    customers = sales[["customer_id", "region"]].drop_duplicates().sort_values("customer_id")

    products = (
        sales.groupby(["product_id", "product_name", "category"], as_index=False)["unit_price"]
        .mean()
        .rename(columns={"unit_price": "unit_price"})
        .sort_values("product_id")
    )
    products["unit_price"] = products["unit_price"].round(2)

    fact_sales = sales[
        [
            "order_id",
            "order_date",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "total_price",
            "sales_channel",
        ]
    ].copy()
    fact_sales["order_date"] = pd.to_datetime(fact_sales["order_date"]).dt.strftime("%Y-%m-%d")

    customers.to_sql("customers", connection, if_exists="append", index=False)
    products.to_sql("products", connection, if_exists="append", index=False)
    fact_sales.to_sql("sales", connection, if_exists="append", index=False)


def validate_load(connection: sqlite3.Connection) -> dict[str, int]:
    cursor = connection.cursor()
    checks = {}
    for table_name in ["customers", "products", "sales"]:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        checks[table_name] = int(count)
    return checks


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing source CSV: {DATA_PATH}")

    sales = load_sales_csv(DATA_PATH)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        create_database(connection)
        load_dimensions_and_fact(connection, sales)
        checks = validate_load(connection)

    print("SQLite database created successfully.")
    print(f"Database file: {DB_PATH}")
    print(f"Customers: {checks['customers']}")
    print(f"Products: {checks['products']}")
    print(f"Sales rows: {checks['sales']}")


if __name__ == "__main__":
    main()
