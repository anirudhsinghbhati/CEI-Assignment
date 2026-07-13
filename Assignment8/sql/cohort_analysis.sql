
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),
customer_orders_elapsed AS (
    SELECT DISTINCT
        o.customer_id,
        cc.cohort_month,
        (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', cc.cohort_month || '-01') AS INTEGER)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', cc.cohort_month || '-01') AS INTEGER)) AS months_elapsed
    FROM orders o
    JOIN customer_cohorts cc ON o.customer_id = cc.customer_id
)
SELECT 
    cs.cohort_month,
    cs.cohort_size,
    COUNT(DISTINCT CASE WHEN coe.months_elapsed = 0 THEN coe.customer_id END) AS month_0_active_users,
    COUNT(DISTINCT CASE WHEN coe.months_elapsed = 1 THEN coe.customer_id END) AS month_1_active_users,
    COUNT(DISTINCT CASE WHEN coe.months_elapsed = 2 THEN coe.customer_id END) AS month_2_active_users,
    COUNT(DISTINCT CASE WHEN coe.months_elapsed = 3 THEN coe.customer_id END) AS month_3_active_users,
    
    ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 0 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_0_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 1 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 2 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_2_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 3 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_3_retention_pct
FROM cohort_sizes cs
LEFT JOIN customer_orders_elapsed coe ON cs.cohort_month = coe.cohort_month
GROUP BY cs.cohort_month, cs.cohort_size
ORDER BY cs.cohort_month;


-- 2. Cohort Retention Analysis (defined by FIRST PURCHASE MONTH)
WITH first_purchase_months AS (
    SELECT 
        customer_id,
        MIN(strftime('%Y-%m', order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(customer_id) AS cohort_size
    FROM first_purchase_months
    GROUP BY cohort_month
),
customer_activity_months AS (
    SELECT DISTINCT
        o.customer_id,
        fpm.cohort_month,
        (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', fpm.cohort_month || '-01') AS INTEGER)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', fpm.cohort_month || '-01') AS INTEGER)) AS months_elapsed
    FROM orders o
    JOIN first_purchase_months fpm ON o.customer_id = fpm.customer_id
)
SELECT 
    cs.cohort_month,
    cs.cohort_size,
    COUNT(DISTINCT CASE WHEN cam.months_elapsed = 0 THEN cam.customer_id END) AS month_0_active_users,
    COUNT(DISTINCT CASE WHEN cam.months_elapsed = 1 THEN cam.customer_id END) AS month_1_active_users,
    COUNT(DISTINCT CASE WHEN cam.months_elapsed = 2 THEN cam.customer_id END) AS month_2_active_users,
    COUNT(DISTINCT CASE WHEN cam.months_elapsed = 3 THEN cam.customer_id END) AS month_3_active_users,
    
    ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 0 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_0_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 1 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 2 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_2_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 3 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 2) AS month_3_retention_pct
FROM cohort_sizes cs
LEFT JOIN customer_activity_months cam ON cs.cohort_month = cam.cohort_month
GROUP BY cs.cohort_month, cs.cohort_size
ORDER BY cs.cohort_month;


-- 3. Identify Churned vs Repeat Customers
WITH customer_orders_summary AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        COUNT(o.order_id) AS total_orders,
        MAX(o.order_date) AS last_order_date,
        (julianday((SELECT MAX(order_date) FROM orders)) - julianday(MAX(o.order_date))) AS days_since_last_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT 
    customer_id,
    customer_name,
    total_orders,
    last_order_date,
    ROUND(days_since_last_order, 1) AS days_since_last_order,
    CASE 
        WHEN total_orders = 0 THEN 'Never Ordered'
        WHEN total_orders > 1 AND days_since_last_order <= 90 THEN 'Active Repeat'
        WHEN total_orders > 1 AND days_since_last_order > 90 THEN 'Churned Repeat'
        WHEN total_orders = 1 AND days_since_last_order <= 90 THEN 'Active One-Time'
        WHEN total_orders = 1 AND days_since_last_order > 90 THEN 'Churned One-Time'
    END AS customer_status
FROM customer_orders_summary
ORDER BY total_orders DESC;

