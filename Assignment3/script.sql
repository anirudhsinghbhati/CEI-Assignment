-- 1. Create Core Tables
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    segment VARCHAR(50)
);
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(50),
    sub_category VARCHAR(50)
);
CREATE TABLE orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    order_date DATE,
    sales DECIMAL(10, 2),
    quantity INT,
    discount DECIMAL(4, 2),
    profit DECIMAL(10, 2),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


-- 2. Populate unique customers
INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT Customer_ID, Customer_Name, Segment
FROM superstore_raw;

INSERT INTO products (product_id, product_name, category, sub_category)
SELECT 
    `Product_ID`, 
    MAX(`Product_Name`), 
    MAX(`Category`), 
    MAX(`Sub_Category`)
FROM superstore_raw
GROUP BY `Product_ID`;

INSERT INTO customers (customer_id, customer_name, segment)
SELECT 
    `Customer_ID`, 
    MAX(`Customer_Name`), 
    MAX(`Segment`)
FROM superstore_raw
GROUP BY `Customer_ID`;

INSERT INTO orders (order_id, customer_id, product_id, order_date, sales, quantity, discount, profit)
SELECT 
    Order_ID, 
    MAX(Customer_ID), 
    Product_ID, 
    MAX(order_date),  -- Added MAX() here to satisfy only_full_group_by rules
    SUM(Sales),       
    SUM(Quantity),    
    MAX(Discount), 
    SUM(Profit)       
FROM superstore_raw
GROUP BY Order_ID, Product_ID;

-- 3.Filter data using Subqueries
-- 3.1 Subquery to find items with above-average sales
SELECT order_id, product_id, sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;

-- 3.2 To find the highest order for each customer
WITH OrderTotals AS (
    -- Group items to get true order totals
    SELECT customer_id, order_id, SUM(sales) AS total_order_sales
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT 
    c.customer_name,
    ot1.order_id,
    ROUND(ot1.total_order_sales, 2) AS highest_order_value
FROM OrderTotals ot1
JOIN customers c ON ot1.customer_id = c.customer_id
WHERE ot1.total_order_sales = (
    -- Correlated subquery: Finds the max order value for THIS specific customer
    SELECT MAX(ot2.total_order_sales)
    FROM OrderTotals ot2
    WHERE ot2.customer_id = ot1.customer_id
)
ORDER BY highest_order_value DESC;

-- 4. Use CTEs to compute aggregations (total sales per customer)
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_customer_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, cs.total_customer_sales
FROM CustomerSales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_customer_sales DESC;

-- 5. Apply window functions (ROW_NUMBER, RANK)
SELECT 
    order_id,
    product_id,
    sales,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY sales DESC) AS row_num_rank,
    RANK() OVER (PARTITION BY order_id ORDER BY sales DESC) AS gap_rank
FROM orders
WHERE order_id IN ('CA-2016-152156', 'CA-2016-138688') 
ORDER BY order_id, sales DESC;


-- 6. Combine JOIN + CTE + Window Functions for final result (customer, total sales, rank)
WITH CustomerRevenueCTE AS (
    -- Step 1: Use a CTE to aggregate all gross sales per unique customer identifier
    SELECT 
        customer_id,
        SUM(sales) AS total_sales,
        COUNT(DISTINCT order_id) AS transaction_count
    FROM orders
    GROUP BY customer_id
)
-- Step 2: Extract details, JOIN tables, and apply the Window Function
SELECT 
    c.customer_name,
    c.segment,
    ROUND(cr.total_sales, 2) AS aggregate_revenue,
    cr.transaction_count,
    -- Step 3: Apply the RANK() Window Function over the aggregated CTE metrics
    RANK() OVER (ORDER BY cr.total_sales DESC) AS customer_rank
FROM CustomerRevenueCTE cr
JOIN customers c ON cr.customer_id = c.customer_id
ORDER BY customer_rank ASC;


-- 7. Solve business queries (top customers, low customers, single-order customers, above-average sales).
-- 7.1 Top Customers
WITH CustomerSpend AS (
    SELECT 
        customer_id,
        SUM(sales) AS total_spent,
        COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name,
    c.segment,
    ROUND(cs.total_spent, 2) AS lifetime_value,
    cs.total_orders,
    DENSE_RANK() OVER (ORDER BY cs.total_spent DESC) as vip_rank
FROM CustomerSpend cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY vip_rank ASC
LIMIT 10;

-- 7.2 Low Customers
WITH CustomerSpend AS (
    SELECT 
        customer_id,
        SUM(sales) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name,
    c.segment,
    ROUND(cs.total_spent, 2) AS total_spent,
    RANK() OVER (ORDER BY cs.total_spent ASC) as bottom_rank
FROM CustomerSpend cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY bottom_rank ASC
LIMIT 10;

-- 7.3 Single-Order Customers
SELECT 
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.sales), 2) AS total_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY total_order_value DESC;

-- 7.4 Above-Average Sales Transactions
SELECT 
    o.order_id,
    c.customer_name,
    p.product_name,
    ROUND(o.sales, 2) AS transaction_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.sales > (SELECT AVG(sales) FROM orders)
ORDER BY o.sales DESC;