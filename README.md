# Sales Analytics End-to-End Portfolio Project

This project simulates a realistic retail sales environment across two full years and demonstrates a complete analytics workflow:

- Synthetic data generation in Python
- CSV ingestion into SQLite
- Exploratory and business analysis in Python with `pandas`
- Visualization output for reporting
- Power BI dashboard design for stakeholder consumption

## Portfolio snapshot

This project answers a practical retail analytics question:

"How are revenue, product mix, region performance, and channel performance changing over time, and where should the business focus next?"

### Core KPIs tracked

- Total Revenue
- Total Orders
- Average Order Value
- Unique Customers
- Units Sold

### Business questions answered

- Which product categories generate the most revenue?
- Which region underperforms and may need targeted action?
- How strong is seasonality across the two-year period?
- Does `Online` outperform `Store`, and by how much?
- Which products drive the largest share of revenue?
- Is order volume concentrated in low-ticket or high-ticket categories?

## Screenshots

Main dashboard:

![Sales dashboard](/C:/Users/tomas/Documents/New%20project/outputs/sales_analysis_dashboard.png)

KPI overview:

![KPI overview](/C:/Users/tomas/Documents/New%20project/outputs/screenshots/01_kpi_overview.png)

Monthly revenue trend:

![Monthly revenue trend](/C:/Users/tomas/Documents/New%20project/outputs/screenshots/02_monthly_revenue_trend.png)

Revenue by category:

![Revenue by category](/C:/Users/tomas/Documents/New%20project/outputs/screenshots/03_revenue_by_category.png)

Revenue by region:

![Revenue by region](/C:/Users/tomas/Documents/New%20project/outputs/screenshots/04_revenue_by_region.png)

The dataset includes 30,000 sales records from `2024-01-01` to `2025-12-31` and was intentionally designed with:

- Q4 seasonality spikes
- Different price bands across categories
- Uneven regional performance
- Distinct online vs store channel behavior
- Product popularity differences instead of pure random sampling

## Project structure

```text
New project/
|-- data/
|   |-- sales_analytics.db
|   `-- sales_data.csv
|-- dashboard/
|   `-- power_bi_dashboard_guide.md
|-- notebooks/
|   `-- README.md
|-- outputs/
|   |-- analysis_summary.csv
|   |-- kpis.csv
|   |-- monthly_revenue.csv
|   |-- revenue_by_category.csv
|   |-- revenue_by_region.csv
|   |-- sales_analysis_dashboard.png
|   |-- sales_channel_comparison.csv
|   |-- screenshots/
|   `-- top_10_products.csv
|-- scripts/
|   |-- analyze_sales.py
|   |-- generate_sales_data.py
|   `-- load_to_sqlite.py
|-- sql/
|   |-- 01_create_schema.sql
|   |-- 02_import_sales_data.sql
|   `-- 03_analytics_queries.sql
|-- requirements.txt
`-- README.md
```

## 1. Synthetic data generation

The generator script creates realistic transactional sales data with the following fields:

- `order_id`
- `order_date`
- `customer_id`
- `product_id`
- `product_name`
- `category`
- `quantity`
- `unit_price`
- `total_price`
- `region`
- `sales_channel`

### Logic used to make the data realistic

- Sales volume is weighted by day rather than uniformly random
- Q4 receives the strongest uplift, with November and December peaking
- Category mix is controlled with weighted product popularity
- Unit prices differ materially across categories
- Online/store mix depends on region
- Quantity distributions differ by category and channel
- Prices vary slightly over time to simulate promotions and seasonal pricing

### Run the generator

```powershell
python scripts/generate_sales_data.py
```

Output:

- [sales_data.csv](C:/Users/tomas/Documents/New%20project/data/sales_data.csv)

## 2. SQLite schema and import

The SQLite model is intentionally normalized into:

- `customers`
- `products`
- `sales`

### Files

- [01_create_schema.sql](C:/Users/tomas/Documents/New%20project/sql/01_create_schema.sql)
- [02_import_sales_data.sql](C:/Users/tomas/Documents/New%20project/sql/02_import_sales_data.sql)
- [03_analytics_queries.sql](C:/Users/tomas/Documents/New%20project/sql/03_analytics_queries.sql)
- [load_to_sqlite.py](C:/Users/tomas/Documents/New%20project/scripts/load_to_sqlite.py)

### Import workflow

1. Generate `sales_data.csv`
2. Run `scripts/load_to_sqlite.py`
3. This creates [sales_analytics.db](C:/Users/tomas/Documents/New%20project/data/sales_analytics.db)
4. Use `03_analytics_queries.sql` for validation in any SQLite client

### Create the SQLite database

```powershell
python scripts/load_to_sqlite.py
```

## 3. Python analysis

The analysis script reads the sales data, calculates portfolio-ready KPIs, exports summary tables, and generates a dashboard image.

### Analyses included

- Monthly revenue trends
- Top 10 products by revenue
- Revenue by category
- Revenue by region
- Sales channel comparison
- Average order value

### Run the analysis

```powershell
python scripts/analyze_sales.py --show
```

Outputs:

- [kpis.csv](C:/Users/tomas/Documents/New%20project/outputs/kpis.csv)
- [monthly_revenue.csv](C:/Users/tomas/Documents/New%20project/outputs/monthly_revenue.csv)
- [revenue_by_category.csv](C:/Users/tomas/Documents/New%20project/outputs/revenue_by_category.csv)
- [revenue_by_region.csv](C:/Users/tomas/Documents/New%20project/outputs/revenue_by_region.csv)
- [sales_channel_comparison.csv](C:/Users/tomas/Documents/New%20project/outputs/sales_channel_comparison.csv)
- [top_10_products.csv](C:/Users/tomas/Documents/New%20project/outputs/top_10_products.csv)
- [sales_analysis_dashboard.png](C:/Users/tomas/Documents/New%20project/outputs/sales_analysis_dashboard.png)
- [screenshots](C:/Users/tomas/Documents/New%20project/outputs/screenshots)

## 4. Power BI dashboard design

Use the guide in [power_bi_dashboard_guide.md](C:/Users/tomas/Documents/New%20project/dashboard/power_bi_dashboard_guide.md) to build a one-page dashboard with:

- KPI cards: Total Revenue, Total Orders, Average Order Value
- Monthly revenue trend line
- Revenue by category bar chart
- Revenue by region bar chart
- Sales channel comparison visual
- Top products table
- Filters for date, region, category, and sales channel

## 5. Key business insights from the generated dataset

Based on the current generated outputs:

1. Electronics is the dominant revenue driver with `$5.85M`, contributing roughly 54% of total revenue.
2. North is the strongest region at `$3.41M`, while East is the weakest at `$2.32M`, showing a meaningful geographic performance gap.
3. Online generates more revenue overall (`$6.09M`) than Store (`$4.76M`), but Store has a slightly higher average order value.
4. Q4 is the clearest seasonal peak, with the strongest months concentrated in November and December and `2025-12` reaching `$814.0K`.
5. Premium electronics drive outsized value. `Gaming Laptop` and `4K Smart TV` are the top two products by revenue by a wide margin.
6. Clothing produces the highest order count, but not the highest revenue, which suggests it is volume-led while Electronics is price-led.

## 6. Portfolio positioning

This project is suitable for showcasing:

- Data engineering fundamentals through CSV-to-SQLite ingestion
- Analytical thinking through trend and segmentation analysis
- Business intelligence design through Power BI planning
- Python automation for repeatable analytics workflows

### Recommended CV / GitHub framing

You can describe this project as:

"Built an end-to-end sales analytics project using Python, SQLite, and Power BI-ready outputs. Generated two years of synthetic transactional sales data, modeled the data into a relational schema, automated KPI reporting, and produced visual analysis assets for portfolio presentation."

## 7. Notes for production polish

- Parameterize file paths with environment variables
- Add database load automation with `sqlalchemy`
- Add unit tests for data quality checks
- Extend the model with customer demographics and returns data
