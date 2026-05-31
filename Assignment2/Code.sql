-- 1: Load Dataset into Database
create database mydb;
use mydb;

CREATE TABLE customers ( 
    customer_id   INT           PRIMARY KEY, 
    first_name    VARCHAR(50)   NOT NULL, 
    last_name     VARCHAR(50)   NOT NULL, 
    email         VARCHAR(100)  UNIQUE NOT NULL, 
    city          VARCHAR(50)   NOT NULL, 
    state         VARCHAR(50)   NOT NULL, 
    join_date     DATE          NOT NULL, 
    is_premium    BOOLEAN       DEFAULT FALSE 
);

-- Index for filtering by city/state 
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_state ON customers(state);

CREATE TABLE products ( 
    product_id    INT           PRIMARY KEY, 
    product_name  VARCHAR(100)  NOT NULL, 
    category      VARCHAR(50)   NOT NULL, 
    brand         VARCHAR(50)   NOT NULL, 
    unit_price    DECIMAL(10,2) NOT NULL  CHECK (unit_price > 0), 
    stock_qty     INT           NOT NULL  DEFAULT 0  CHECK (stock_qty >= 0) 
);

-- Index for filtering by category 
CREATE INDEX idx_products_category ON products(category);

CREATE TABLE orders ( 
    order_id      INT           PRIMARY KEY, 
    customer_id   INT           NOT NULL, 
    order_date    DATE          NOT NULL,
    status        VARCHAR(20)   NOT NULL  DEFAULT 'Pending' 
                  CHECK (status IN ('Pending','Shipped','Delivered','Cancelled')), 
    total_amount  DECIMAL(12,2) NOT NULL  CHECK (total_amount >= 0), 
     
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
);

-- Index for date-based filtering and sorting 
CREATE INDEX idx_orders_date ON orders(order_date); 
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items ( 
    item_id       INT           PRIMARY KEY, 
    order_id      INT           NOT NULL, 
    product_id    INT           NOT NULL, 
    quantity      INT           NOT NULL  CHECK (quantity > 0), 
    unit_price    DECIMAL(10,2) NOT NULL  CHECK (unit_price > 0), 
    discount_pct  DECIMAL(5,2)  DEFAULT 0 CHECK (discount_pct BETWEEN 0 AND 100), 
     
    FOREIGN KEY (order_id)   REFERENCES orders(order_id), 
    FOREIGN KEY (product_id) REFERENCES products(product_id) 
);

-- ========== INSERT: customers ========== 
INSERT INTO customers VALUES 
(101, 'Aarav',  'Sharma', 'aarav.s@email.com',  'Mumbai',    'Maharashtra', '2024-01-15', TRUE), 
(102, 'Priya',  'Patel',  'priya.p@email.com',  'Ahmedabad', 'Gujarat',     '2024-02-20', FALSE), 
(103, 'Rohan',  'Gupta',  'rohan.g@email.com',  'Delhi',     'Delhi',       '2024-03-10', TRUE), 
(104, 'Sneha',  'Reddy',  'sneha.r@email.com',  'Hyderabad', 'Telangana',   '2024-04-05', FALSE), 
(105, 'Vikram', 'Singh',  'vikram.s@email.com', 'Jaipur',    'Rajasthan',   '2024-05-12', TRUE), 
(106, 'Ananya', 'Iyer',   'ananya.i@email.com', 'Chennai',   'Tamil Nadu',  '2024-06-18', FALSE), 
(107, 'Karan',  'Mehta',  'karan.m@email.com',  'Pune',      'Maharashtra', '2024-07-22', TRUE), 
(108, 'Divya',  'Nair',   'divya.n@email.com',  'Kochi',     'Kerala',      '2024-08-30', FALSE);

-- ========== INSERT: products ========== 
INSERT INTO products VALUES 
(201, 'Wireless Earbuds',     'Electronics', 'BoAt',          1499.00, 250), 
(202, 'Cotton T-Shirt',       'Clothing',    'Levis',         799.00,  500), 
(203, 'Smart Watch',          'Electronics', 'Noise',         2999.00, 150), 
(204, 'Running Shoes',        'Clothing',    'Nike',          4599.00, 120), 
(205, 'Bluetooth Speaker',    'Electronics', 'JBL',           3499.00, 200), 
(206, 'Bedsheet Set',         'Home',        'Spaces',        1299.00, 300), 
(207, 'Laptop Stand',         'Electronics', 'AmazonBasics',  899.00,  180), 
(208, 'Cushion Covers (Set)', 'Home',        'HomeCenter',    599.00,  400);  

-- ========== INSERT: orders ========== 
INSERT INTO orders VALUES 
(1001, 101, '2024-08-01', 'Delivered',  4498.00), 
(1002, 102, '2024-08-03', 'Delivered',  799.00), 
(1003, 103, '2024-08-05', 'Shipped',    7498.00), 
(1004, 101, '2024-08-10', 'Delivered',  3499.00), 
(1005, 104, '2024-08-12', 'Cancelled',  2999.00), 
(1006, 105, '2024-08-15', 'Delivered',  5898.00), 
(1007, 106, '2024-08-18', 'Pending',    1299.00), 
(1008, 103, '2024-08-20', 'Delivered',  899.00), 
(1009, 107, '2024-08-25', 'Shipped',    6098.00), 
(1010, 108, '2024-08-28', 'Delivered',  1598.00); 

-- ========== INSERT: order_items ========== 
INSERT INTO order_items VALUES 
(5001, 1001, 201, 2, 1499.00, 0), 
(5002, 1001, 207, 1, 899.00,  10), 
(5003, 1002, 202, 1, 799.00,  0), 
(5004, 1003, 203, 1, 2999.00, 0), 
(5005, 1003, 204, 1, 4599.00, 5), 
(5006, 1004, 205, 1, 3499.00, 0), 
(5007, 1005, 203, 1, 2999.00, 0), 
(5008, 1006, 201, 1, 1499.00, 10), 
(5009, 1006, 204, 1, 4599.00, 5), 
(5010, 1007, 206, 1, 1299.00, 0), 
(5011, 1008, 207, 1, 899.00,  0), 
(5012, 1009, 205, 1, 3499.00, 0), 
(5013, 1009, 208, 2, 599.00,  15), 
(5014, 1010, 206, 1, 1299.00, 0), 
(5015, 1010, 208, 1, 599.00,  0); 
-- ===================================== --

-- 2: Explore Database

-- Schema Information
DESCRIBE customers;
DESCRIBE products;
DESCRIBE orders;
DESCRIBE order_items;

-- Row Counts
SELECT COUNT(*) AS customer_count FROM customers;
-- result 8
SELECT COUNT(*) AS product_count FROM products;
-- result 8
SELECT COUNT(*) AS order_count FROM orders;
-- result 10
SELECT COUNT(*) AS order_item_count FROM order_items;
-- result 10

-- Sample Data
SELECT * FROM customers LIMIT 5;
SELECT * FROM products LIMIT 5;
SELECT * FROM orders LIMIT 5;
SELECT * FROM order_items LIMIT 5;
-- ===================================== --

-- 3: WHERE Filtering

-- Orders Delivered 
SELECT *
FROM orders
WHERE status='Delivered';

-- Electronics Products Above ₹2000
SELECT *
FROM products
WHERE category='Electronics'
AND unit_price > 2000;

-- Maharashtra Customers
SELECT *
FROM customers
WHERE state='Maharashtra'
AND join_date BETWEEN '2024-01-01' AND '2024-12-31';

-- Orders Between Dates
SELECT *
FROM orders
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25'
AND status <> 'Cancelled';

-- 4: GROUP BY Aggregations

-- Total Orders
SELECT COUNT(*) AS total_orders
FROM orders;

-- Delivered Revenue
SELECT SUM(total_amount) AS delivered_revenue
FROM orders
WHERE status='Delivered';

-- Average Price by Category
SELECT
    category,
    ROUND(AVG(unit_price),2) AS avg_price
FROM products
GROUP BY category;

-- Revenue by Status
SELECT
    status,
    COUNT(*) AS orders_count,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY status
ORDER BY revenue DESC;

-- Min and Max Product Price per Category
SELECT
    category,
    MIN(unit_price) AS cheapest,
    MAX(unit_price) AS expensive
FROM products
GROUP BY category;

-- Categories With Average Price > ₹2000
SELECT
    category,
    AVG(unit_price) avg_price
FROM products
GROUP BY category
HAVING AVG(unit_price) > 2000;

-- 5: Sorting and Top Results

-- Top 5 Products by Revenue
SELECT
    p.product_name,
    SUM(oi.quantity * oi.unit_price *
        (1-oi.discount_pct/100)) AS revenue
FROM order_items oi
JOIN products p
ON oi.product_id=p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 5;

-- Top Categories by Revenue
SELECT
    p.category,
    SUM(oi.quantity*oi.unit_price*
        (1-oi.discount_pct/100)) revenue
FROM order_items oi
JOIN products p
ON oi.product_id=p.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 6: Business Use Cases

-- Monthly Sales Trend
SELECT
    DATE_FORMAT(order_date,'%Y-%m') AS month,
    SUM(total_amount) AS sales
FROM orders
GROUP BY month;

-- Top Customers by Spending
SELECT
    c.customer_id,
    CONCAT(c.first_name,' ',c.last_name) customer_name,
    SUM(o.total_amount) total_spent
FROM customers c
JOIN orders o
ON c.customer_id=o.customer_id
GROUP BY c.customer_id, customer_name
ORDER BY total_spent DESC
LIMIT 5;

-- Detect Duplicate Emails
SELECT
    email,
    COUNT(*)
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;

-- 7: Data Validation
-- Check Total Rows
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;

-- Check Orders Without Customers
SELECT *
FROM orders o
LEFT JOIN customers c
ON o.customer_id=c.customer_id
WHERE c.customer_id IS NULL;

-- Check Order Items Without Products
SELECT *
FROM order_items oi
LEFT JOIN products p
ON oi.product_id=p.product_id
WHERE p.product_id IS NULL;

-- Check Negative Prices
SELECT *
FROM products
WHERE unit_price <= 0;
