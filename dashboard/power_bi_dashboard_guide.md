# Power BI Dashboard Design

## Recommended layout

Use a single-page executive dashboard with a left-to-right reading flow:

1. Top KPI cards
2. Monthly trend chart
3. Category and region performance charts
4. Sales channel comparison
5. Top products table
6. Slicer panel on the left or across the top

## Data model

Import the following tables:

- `sales_data.csv` for a quick prototype, or
- SQLite tables: `sales`, `customers`, `products` for a lightweight local model

Recommended relationships:

- `sales.customer_id` -> `customers.customer_id`
- `sales.product_id` -> `products.product_id`

Create a dedicated calendar table in Power BI and relate it to `sales[order_date]`.

## KPIs

Add three KPI cards at the top:

- Total Revenue
- Total Orders
- Average Order Value

Suggested DAX measures:

```DAX
Total Revenue = SUM(sales[total_price])

Total Orders = DISTINCTCOUNT(sales[order_id])

Average Order Value = DIVIDE([Total Revenue], [Total Orders])
```

Optional supporting KPIs:

- Units Sold = SUM(sales[quantity])
- Unique Customers = DISTINCTCOUNT(sales[customer_id])

## Visuals

### 1. Monthly revenue trend

- Visual: Line chart
- Axis: `order_date` by month
- Values: `Total Revenue`
- Add a rolling 3-month average if desired

### 2. Revenue by category

- Visual: Clustered bar chart
- Axis: `category`
- Values: `Total Revenue`
- Sort descending by revenue

### 3. Revenue by region

- Visual: Clustered bar chart
- Axis: `region`
- Values: `Total Revenue`

### 4. Sales channel comparison

- Visual: Column chart or donut chart
- Legend/Axis: `sales_channel`
- Values: `Total Revenue`
- Tooltip: `Average Order Value`, `Total Orders`

### 5. Top products table

- Visual: Table
- Columns:
  - `product_name`
  - `category`
  - `Total Revenue`
  - `Units Sold`
  - `Total Orders`
- Apply Top N filter = 10 by `Total Revenue`

## Filters / slicers

Include slicers for:

- Date
- Region
- Category
- Sales Channel

Optional:

- Product Name

## Design recommendations

- Use a clean light theme with 1 accent color per business dimension
- Keep category, region, and channel colors consistent across visuals
- Add a tooltip page for product detail
- Add drill-through from product table to product-level trend page if you want a second dashboard page

## Portfolio tip

Show both versions in your portfolio:

- Version 1: CSV import into Power BI for quick prototype
- Version 2: SQLite-backed local model for a lightweight end-to-end workflow
