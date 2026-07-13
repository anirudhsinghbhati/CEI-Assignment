-- 1. Total revenue per category

SELECT 
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_type,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_spend,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY total_spend DESC
LIMIT 10;


-- 3. Month-wise order count for the last 12 months

SELECT 
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(o.order_id) AS order_count
FROM orders o
WHERE o.order_date >= date((SELECT MAX(order_date) FROM orders), '-12 months')
GROUP BY order_month
ORDER BY order_month DESC;



-- 4. Find customers who placed orders but never had any item delivered

   SELECT c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders_placed
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE status = 'DELIVERED'
)
GROUP BY c.customer_id, c.customer_name
ORDER BY total_orders_placed DESC;


-- 5. Products that were ordered but had more returns than purchases

SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS units_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS units_returned,
    SUM(oi.quantity) AS net_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(oi.quantity) < 0;


-- 6. Calculate the return rate (returned items / total items purchased) per category

SELECT 
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS units_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS units_returned,
    ROUND(
        SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0), 
        2
    ) AS return_rate_percent
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_percent DESC;


-- 7. Total revenue per customer, per category, per month (Joins across all tables)
SELECT 
    c.customer_id,
    c.customer_name,
    p.category,
    strftime('%Y-%m', o.order_date) AS order_month,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY c.customer_id, c.customer_name, p.category, order_month
ORDER BY total_revenue DESC;


-- 8. Top products by quantity sold and revenue
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_quantity_sold,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC, total_quantity_sold DESC;


-- 9. Average order value (AOV) by customer segment (purchase frequency segment)
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS num_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
),
customer_segmentation AS (
    SELECT 
        customer_id,
        CASE 
            WHEN num_orders = 1 THEN 'One-time'
            WHEN num_orders BETWEEN 2 AND 4 THEN 'Occasional'
            WHEN num_orders >= 5 THEN 'Loyal'
            ELSE 'No Orders'
        END AS frequency_segment
    FROM customer_stats
),
order_totals AS (
    SELECT 
        o.order_id,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_id, o.customer_id
)
SELECT 
    seg.frequency_segment AS customer_segment,
    COUNT(DISTINCT ot.order_id) AS total_orders,
    ROUND(SUM(ot.order_value), 2) AS total_revenue,
    ROUND(AVG(ot.order_value), 2) AS average_order_value
FROM order_totals ot
JOIN customer_segmentation seg ON ot.customer_id = seg.customer_id
WHERE seg.frequency_segment != 'No Orders'
GROUP BY seg.frequency_segment
ORDER BY average_order_value DESC;

