-- SQLite does not support direct CSV import inside a portable SQL script.
-- Use the Python loader instead:
--   python scripts/load_to_sqlite.py
--
-- If you want to import manually in the sqlite3 CLI:
--   .mode csv
--   .import data/sales_data.csv staging_sales
--
-- Then populate the dimensional tables and fact table with statements like:

DROP TABLE IF EXISTS staging_sales;

CREATE TABLE staging_sales (
    order_id TEXT,
    order_date TEXT,
    customer_id TEXT,
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    quantity INTEGER,
    unit_price NUMERIC,
    total_price NUMERIC,
    region TEXT,
    sales_channel TEXT
);

INSERT OR IGNORE INTO customers (customer_id, region)
SELECT DISTINCT customer_id, region
FROM staging_sales;

INSERT OR IGNORE INTO products (product_id, product_name, category, unit_price)
SELECT product_id, product_name, category, AVG(unit_price)
FROM staging_sales
GROUP BY product_id, product_name, category;

INSERT OR IGNORE INTO sales (
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_price,
    sales_channel
)
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_price,
    sales_channel
FROM staging_sales;
