-- Monthly revenue trend
SELECT
    strftime('%Y-%m-01', order_date) AS month_start,
    SUM(total_price) AS monthly_revenue
FROM sales
GROUP BY 1
ORDER BY 1;

-- Top 10 products by revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(s.total_price) AS total_revenue,
    SUM(s.quantity) AS total_units_sold,
    COUNT(*) AS order_count
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY 1, 2, 3
ORDER BY total_revenue DESC
LIMIT 10;

-- Revenue by category
SELECT
    p.category,
    SUM(s.total_price) AS total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY 1
ORDER BY total_revenue DESC;

-- Revenue by region
SELECT
    c.region,
    SUM(s.total_price) AS total_revenue
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
GROUP BY 1
ORDER BY total_revenue DESC;

-- Sales channel comparison
SELECT
    sales_channel,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(total_price) AS total_revenue,
    AVG(total_price) AS average_order_value
FROM sales
GROUP BY 1
ORDER BY total_revenue DESC;
