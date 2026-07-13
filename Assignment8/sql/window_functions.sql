
-- 7. Running Totals with Window Functions

WITH daily_region_revenue AS (
    SELECT 
        o.region_code,
        date(o.order_date) AS order_date_day,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.region_code, order_date_day
)
SELECT 
    region_code,
    order_date_day AS order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code 
        ORDER BY order_date_day 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily_region_revenue
ORDER BY region_code, order_date_day;



-- 8. Ranking with DENSE_RANK
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;



-- 9. LAG/LEAD Analysis

WITH order_gaps AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date,
        julianday(order_date) - julianday(LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)) AS days_gap
    FROM orders
),
customer_avg_gap AS (
    SELECT 
        customer_id,
        AVG(days_gap) AS avg_gap
    FROM order_gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT 
    og.customer_id,
    og.order_date,
    og.previous_order_date,
    ROUND(og.days_gap, 2) AS days_gap,
    ROUND(cag.avg_gap, 2) AS avg_gap,
    CASE 
        WHEN cag.avg_gap > 30 THEN 'At Risk' 
        ELSE 'Active' 
    END AS status_flag
FROM order_gaps og
LEFT JOIN customer_avg_gap cag ON og.customer_id = cag.customer_id
ORDER BY og.customer_id, og.order_date;



-- 10. CTE with Multiple Levels

WITH monthly_customer_revenue AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', order_date) AS order_month,
        SUM(quantity * unit_price * (1 - discount_percent / 100.0)) AS total_rev
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY customer_id, order_month
),
categorized_customers AS (
    SELECT 
        customer_id,
        order_month,
        total_rev,
        CASE 
            WHEN total_rev > 10000 THEN 'High'
            WHEN total_rev BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS spend_category
    FROM monthly_customer_revenue
)
SELECT 
    order_month,
    spend_category,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(total_rev), 2) AS total_revenue
FROM categorized_customers
GROUP BY order_month, spend_category
ORDER BY order_month DESC, spend_category;


-- 11. NTILE for Segmentation

WITH customer_ltv AS (
    SELECT 
        customer_id,
        SUM(quantity * unit_price * (1 - discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY customer_id
),
quartiled_customers AS (
    SELECT 
        customer_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT 
    customer_id,
    ROUND(total_value, 2) AS total_value,
    quartile,
    CASE 
        WHEN quartile = 1 THEN 'Platinum'
        WHEN quartile = 2 THEN 'Gold'
        WHEN quartile = 3 THEN 'Silver'
        WHEN quartile = 4 THEN 'Bronze'
    END AS quartile_label
FROM quartiled_customers
ORDER BY total_value DESC;



-- 12. Year-over-Year Comparison

WITH monthly_revenue AS (
    SELECT 
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS r_year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS r_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY r_year, r_month
),
yoy_comparison AS (
    SELECT 
        curr.r_year AS year,
        curr.r_month AS month,
        curr.revenue AS revenue,
        prev.revenue AS prev_year_revenue
    FROM monthly_revenue curr
    LEFT JOIN monthly_revenue prev ON curr.r_year = prev.r_year + 1 AND curr.r_month = prev.r_month
)
SELECT 
    year,
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(prev_year_revenue, 2) AS prev_year_revenue,
    CASE 
        WHEN prev_year_revenue IS NULL THEN 'N/A'
        ELSE ROUND(((revenue - prev_year_revenue) * 100.0 / prev_year_revenue), 2) || '%'
    END AS yoy_growth_percent
FROM yoy_comparison
ORDER BY year DESC, month DESC;



-- 13. First/Last Value Analysis

WITH customer_item_sequence AS (
    SELECT 
        o.customer_id,
        p.category,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC, oi.item_id ASC) AS seq_asc,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, oi.item_id DESC) AS seq_desc
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
),
first_purchase AS (
    SELECT customer_id, category AS first_category
    FROM customer_item_sequence
    WHERE seq_asc = 1
),
last_purchase AS (
    SELECT customer_id, category AS last_category
    FROM customer_item_sequence
    WHERE seq_desc = 1
)
SELECT 
    c.customer_id,
    c.customer_name,
    fp.first_category,
    lp.last_category,
    CASE WHEN fp.first_category = lp.last_category THEN 'No' ELSE 'Yes' END AS category_shift
FROM customers c
JOIN first_purchase fp ON c.customer_id = fp.customer_id
JOIN last_purchase lp ON c.customer_id = lp.customer_id
ORDER BY c.customer_id;



-- 14. Cumulative Distribution

WITH customer_rev AS (
    SELECT 
        customer_id,
        SUM(quantity * unit_price * (1 - discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY customer_id
),
total_rev_cte AS (
    SELECT SUM(revenue) AS grand_total FROM customer_rev
),
running_rev AS (
    SELECT 
        cr.customer_id,
        cr.revenue,
        SUM(cr.revenue) OVER (ORDER BY cr.revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
    FROM customer_rev cr
)
SELECT 
    rr.customer_id,
    ROUND(rr.revenue, 2) AS revenue,
    ROUND(rr.cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((rr.cumulative_revenue * 100.0 / (SELECT grand_total FROM total_rev_cte)), 2) AS cumulative_percent
FROM running_rev rr
ORDER BY rr.revenue DESC;



-- 15. Self-Join: 

SELECT 
    oi1.product_id AS product_id_a,
    p1.product_name AS product_a,
    oi2.product_id AS product_id_b,
    p2.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY oi1.product_id, oi2.product_id, p1.product_name, p2.product_name
ORDER BY times_bought_together DESC
LIMIT 20;


-- 16. Rank Customers by Lifetime Value using DENSE_RANK
WITH customer_ltv AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS lifetime_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT 
    customer_id,
    customer_name,
    lifetime_value,
    DENSE_RANK() OVER (ORDER BY lifetime_value DESC) AS ltv_rank
FROM customer_ltv
ORDER BY ltv_rank ASC;


-- 17. 7-Day Moving Average Daily Revenue using AVG() OVER
WITH daily_revenue AS (
    SELECT 
        date(o.order_date) AS order_date_day,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_rev
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY order_date_day
)
SELECT 
    order_date_day AS order_date,
    ROUND(daily_rev, 2) AS daily_revenue,
    ROUND(SUM(daily_rev) OVER (
        ORDER BY order_date_day 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total,
    ROUND(AVG(daily_rev) OVER (
        ORDER BY order_date_day 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS seven_day_moving_avg
FROM daily_revenue
ORDER BY order_date;


-- 18. RFM (Recency, Frequency, Monetary) Customer Segmentation
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        ROUND(julianday((SELECT MAX(order_date) FROM orders)) - julianday(MAX(o.order_date)), 1) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        recency,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency ASC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency DESC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary DESC) AS m_score
    FROM customer_metrics
)
SELECT 
    customer_id,
    customer_name,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    (r_score || '-' || f_score || '-' || m_score) AS rfm_cell,
    CASE 
        WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Core Loyal'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Active Engaged'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'At Risk Loyal'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Lost Customer'
        ELSE 'Regular'
    END AS rfm_segment
FROM rfm_scores
ORDER BY monetary DESC;

