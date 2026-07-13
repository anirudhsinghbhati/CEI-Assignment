import argparse
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"

def get_latest_order_date(cursor):
    cursor.execute("SELECT MAX(order_date) FROM orders")
    res = cursor.fetchone()[0]
    if res:
     
        return datetime.strptime(res.split()[0], "%Y-%m-%d")
    return datetime(2026, 6, 30) 

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: '{date_str}'. Must be YYYY-MM-DD.")

def calculate_previous_period(start_dt, end_dt):
    delta = (end_dt - start_dt).days + 1
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = start_dt - timedelta(days=delta)
    return prev_start_dt, prev_end_dt

def get_period_stats(cursor, start_dt, end_dt):
    start_str = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
    end_str = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
    
    # Total orders
    cursor.execute("""
        SELECT COUNT(order_id) 
        FROM orders 
        WHERE order_date BETWEEN ? AND ?
    """, (start_str, end_str))
    total_orders = cursor.fetchone()[0] or 0
    
    # Net revenue
    cursor.execute("""
        SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) 
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?
    """, (start_str, end_str))
    revenue = cursor.fetchone()[0] or 0.0
    
    # Unique customers
    cursor.execute("""
        SELECT COUNT(DISTINCT customer_id) 
        FROM orders 
        WHERE order_date BETWEEN ? AND ?
    """, (start_str, end_str))
    unique_customers = cursor.fetchone()[0] or 0
    
    return total_orders, round(revenue, 2), unique_customers

def get_top_products(cursor, start_dt, end_dt, limit=3):
    start_str = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
    end_str = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
    
    cursor.execute("""
        SELECT 
            p.product_name,
            p.category,
            SUM(oi.quantity) AS quantity_sold,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS product_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY product_revenue DESC
        LIMIT ?
    """, (start_str, end_str, limit))
    return cursor.fetchall()

def get_breakdown(cursor, report_type, start_dt, end_dt):
    start_str = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
    end_str = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
    
    if report_type == "daily":
        date_format = "%Y-%m-%d"
        group_col = "date(o.order_date)"
    elif report_type == "weekly":
        date_format = "Week %W (%Y)"
        group_col = "strftime('%Y-W%W', o.order_date)"
    else:
        date_format = "%Y-%m"
        group_col = "strftime('%Y-%m', o.order_date)"
        
    query = f"""
        SELECT 
            {group_col} AS time_period,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS period_revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY time_period
        ORDER BY time_period ASC
    """
    cursor.execute(query, (start_str, end_str))
    return cursor.fetchall()

def print_ascii_table(headers, rows):
    if not rows:
        print("No data available.")
        return
        
    # Find column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    # Print border and headers
    row_fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    separator = "-+-".join("-" * w for w in widths)
    
    print(separator)
    print(row_fmt.format(*headers))
    print(separator)
    for row in rows:
        # Convert numeric values to formatted strings 
        formatted_row = []
        for val in row:
            if isinstance(val, float):
                formatted_row.append(f"{val:,.2f}")
            else:
                formatted_row.append(str(val))
        print(row_fmt.format(*formatted_row))
    print(separator)

def generate_revenue_report(cursor, start_dt, end_dt):
    start_str = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
    end_str = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
    
    print("\n" + "=" * 70)
    print(f"             REVENUE REPORT")
    print(f"             Period: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
    print("=" * 70)
    
    # 1. Total revenue per category
    print("\n[TOTAL REVENUE BY CATEGORY]")
    cursor.execute("""
        SELECT 
            p.category,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """, (start_str, end_str))
    print_ascii_table(["Category", "Total Revenue"], cursor.fetchall())
    
    # 2. Total revenue per customer, per category, per month (Top 15 rows)
    print("\n[REVENUE BY CUSTOMER, CATEGORY, MONTH (Top 15)]")
    cursor.execute("""
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
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY c.customer_id, c.customer_name, p.category, order_month
        ORDER BY total_revenue DESC
        LIMIT 15
    """, (start_str, end_str))
    print_ascii_table(["Cust ID", "Customer Name", "Category", "Month", "Revenue"], cursor.fetchall())

def generate_top_customers_report(cursor, start_dt, end_dt):
    start_str = start_dt.strftime("%Y-%m-%d") + " 00:00:00"
    end_str = end_dt.strftime("%Y-%m-%d") + " 23:59:59"
    
    print("\n" + "=" * 70)
    print(f"             TOP CUSTOMERS & RANKINGS REPORT")
    print(f"             Period: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
    print("=" * 70)
    
    # 1. Top 10 customers by total spend
    print("\n[TOP 10 CUSTOMERS BY SPENDING]")
    cursor.execute("""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.customer_type,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_spend,
            COUNT(DISTINCT o.order_id) AS total_orders
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?
        GROUP BY c.customer_id, c.customer_name, c.customer_type
        ORDER BY total_spend DESC
        LIMIT 10
    """, (start_str, end_str))
    print_ascii_table(["Cust ID", "Customer Name", "Type", "Total Spend", "Orders"], cursor.fetchall())

    # 2. Customer rankings by lifetime value using DENSE_RANK()
    print("\n[CUSTOMER DENSE RANK BY LIFETIME VALUE (Top 10)]")
    cursor.execute("""
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
        ORDER BY ltv_rank ASC
        LIMIT 10
    """)
    print_ascii_table(["Cust ID", "Customer Name", "LTV", "Rank"], cursor.fetchall())

def generate_retention_report(cursor):
    print("\n" + "=" * 70)
    print(f"             COHORT RETENTION REPORT")
    print("=" * 70)
    
    # 1. Registration cohorts
    print("\n[COHORT RETENTION BY REGISTRATION MONTH (Top 10 Cohorts)]")
    cursor.execute("""
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
            cs.cohort_month AS Cohort,
            cs.cohort_size AS Size,
            COUNT(DISTINCT CASE WHEN coe.months_elapsed = 0 THEN coe.customer_id END) AS M0,
            COUNT(DISTINCT CASE WHEN coe.months_elapsed = 1 THEN coe.customer_id END) AS M1,
            COUNT(DISTINCT CASE WHEN coe.months_elapsed = 2 THEN coe.customer_id END) AS M2,
            COUNT(DISTINCT CASE WHEN coe.months_elapsed = 3 THEN coe.customer_id END) AS M3,
            ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 1 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M1_Ret,
            ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 2 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M2_Ret,
            ROUND(COUNT(DISTINCT CASE WHEN coe.months_elapsed = 3 THEN coe.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M3_Ret
        FROM cohort_sizes cs
        LEFT JOIN customer_orders_elapsed coe ON cs.cohort_month = coe.cohort_month
        GROUP BY cs.cohort_month, cs.cohort_size
        ORDER BY cs.cohort_month
        LIMIT 10
    """)
    print_ascii_table(["Cohort", "Size", "M0", "M1", "M2", "M3", "M1 Ret %", "M2 Ret %", "M3 Ret %"], cursor.fetchall())

    # 2. First purchase cohorts
    print("\n[COHORT RETENTION BY FIRST PURCHASE MONTH (Top 10 Cohorts)]")
    cursor.execute("""
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
            cs.cohort_month AS Cohort,
            cs.cohort_size AS Size,
            COUNT(DISTINCT CASE WHEN cam.months_elapsed = 0 THEN cam.customer_id END) AS M0,
            COUNT(DISTINCT CASE WHEN cam.months_elapsed = 1 THEN cam.customer_id END) AS M1,
            COUNT(DISTINCT CASE WHEN cam.months_elapsed = 2 THEN cam.customer_id END) AS M2,
            COUNT(DISTINCT CASE WHEN cam.months_elapsed = 3 THEN cam.customer_id END) AS M3,
            ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 1 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M1_Ret,
            ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 2 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M2_Ret,
            ROUND(COUNT(DISTINCT CASE WHEN cam.months_elapsed = 3 THEN cam.customer_id END) * 100.0 / cs.cohort_size, 1) || '%' AS M3_Ret
        FROM cohort_sizes cs
        LEFT JOIN customer_activity_months cam ON cs.cohort_month = cam.cohort_month
        GROUP BY cs.cohort_month, cs.cohort_size
        ORDER BY cs.cohort_month
        LIMIT 10
    """)
    print_ascii_table(["Cohort", "Size", "M0", "M1", "M2", "M3", "M1 Ret %", "M2 Ret %", "M3 Ret %"], cursor.fetchall())

def generate_segmentation_report(cursor):
    print("\n" + "=" * 70)
    print(f"             CUSTOMER SEGMENTATION & RFM SUMMARY REPORT")
    print("=" * 70)
    
    # 1. Purchase frequency segments
    print("\n[AOV BY CUSTOMER SEGMENT (PURCHASE FREQUENCY)]")
    cursor.execute("""
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
            seg.frequency_segment AS segment,
            COUNT(DISTINCT ot.order_id) AS total_orders,
            ROUND(SUM(ot.order_value), 2) AS total_revenue,
            ROUND(AVG(ot.order_value), 2) AS average_order_value
        FROM order_totals ot
        JOIN customer_segmentation seg ON ot.customer_id = seg.customer_id
        WHERE seg.frequency_segment != 'No Orders'
        GROUP BY seg.frequency_segment
        ORDER BY average_order_value DESC
    """)
    print_ascii_table(["Segment", "Total Orders", "Total Rev", "AOV"], cursor.fetchall())

    # 2. RFM segmentation summary
    print("\n[RFM CUSTOMER SEGMENTS SUMMARY]")
    cursor.execute("""
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
        ),
        rfm_segments AS (
            SELECT 
                customer_id,
                customer_name,
                recency,
                frequency,
                monetary,
                r_score,
                f_score,
                m_score,
                CASE 
                    WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Core Loyal'
                    WHEN r_score <= 2 AND f_score <= 2 THEN 'Active Engaged'
                    WHEN r_score >= 3 AND f_score <= 2 THEN 'At Risk Loyal'
                    WHEN r_score >= 3 AND f_score >= 3 THEN 'Lost Customer'
                    ELSE 'Regular'
                END AS rfm_segment
            FROM rfm_scores
        )
        SELECT 
            rfm_segment,
            COUNT(*) AS customer_count,
            ROUND(AVG(recency), 1) AS avg_recency_days,
            ROUND(AVG(frequency), 1) AS avg_frequency,
            ROUND(AVG(monetary), 2) AS avg_spend
        FROM rfm_segments
        GROUP BY rfm_segment
        ORDER BY customer_count DESC
    """)
    print_ascii_table(["RFM Segment", "Cust Count", "Avg Recency", "Avg Freq", "Avg Spend"], cursor.fetchall())

def generate_report(report_type, start_dt, end_dt):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found. Please run 'python scripts/db_setup.py' first.")
        return
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Route to appropriate report generator
        if report_type == "revenue":
            generate_revenue_report(cursor, start_dt, end_dt)
        elif report_type == "top_customers":
            generate_top_customers_report(cursor, start_dt, end_dt)
        elif report_type == "retention":
            generate_retention_report(cursor)
        elif report_type == "segmentation":
            generate_segmentation_report(cursor)
        else:
            # Handle daily/weekly/monthly summary reports
            prev_start_dt, prev_end_dt = calculate_previous_period(start_dt, end_dt)
            curr_orders, curr_rev, curr_cust = get_period_stats(cursor, start_dt, end_dt)
            prev_orders, prev_rev, prev_cust = get_period_stats(cursor, prev_start_dt, prev_end_dt)
            
            def pct_change(curr, prev):
                if prev == 0:
                    return "N/A" if curr == 0 else "+100.0%"
                change = ((curr - prev) * 100.0) / prev
                sign = "+" if change >= 0 else ""
                return f"{sign}{change:.2f}%"

            orders_change = pct_change(curr_orders, prev_orders)
            rev_change = pct_change(curr_rev, prev_rev)
            cust_change = pct_change(curr_cust, prev_cust)
            
            top_products = get_top_products(cursor, start_dt, end_dt)
            breakdown_data = get_breakdown(cursor, report_type, start_dt, end_dt)
            
            print("\n" + "=" * 70)
            print(f"             E-COMMERCE ORDER ANALYTICS SUMMARY REPORT")
            print(f"             Report Type: {report_type.upper()}")
            print(f"             Current Period:  {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
            print(f"             Previous Period: {prev_start_dt.strftime('%Y-%m-%d')} to {prev_end_dt.strftime('%Y-%m-%d')}")
            print("=" * 70)
            
            print("\n[KEY PERFORMANCE METRICS]")
            metric_headers = ["Metric", "Current Period", "Previous Period", "% Change"]
            metric_rows = [
                ["Total Orders", curr_orders, prev_orders, orders_change],
                ["Net Revenue", curr_rev, prev_rev, rev_change],
                ["Unique Customers", curr_cust, prev_cust, cust_change]
            ]
            print_ascii_table(metric_headers, metric_rows)
            
            print("\n[TOP 3 PRODUCTS BY REVENUE]")
            product_headers = ["Product Name", "Category", "Units Sold", "Revenue"]
            print_ascii_table(product_headers, top_products)
            
            print(f"\n[PERIODIC BREAKDOWN ({report_type.upper()})]")
            breakdown_headers = ["Period", "Orders", "Revenue", "Unique Customers"]
            print_ascii_table(breakdown_headers, breakdown_data)
            
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="E-Commerce Order Analytics CLI Reporting Tool")
    parser.add_argument(
        "--report", 
        choices=["daily", "weekly", "monthly", "revenue", "top_customers", "retention", "segmentation"], 
        default="monthly", 
        help="Report type (default: monthly)"
    )
    parser.add_argument(
        "--start-date", 
        type=parse_date, 
        help="Start date for the report range (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", 
        type=parse_date, 
        help="End date for the report range (YYYY-MM-DD)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found. Please run 'python scripts/db_setup.py' first.")
        return
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ref_dt = get_latest_order_date(cursor)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return
    finally:
        if 'conn' in locals():
            conn.close()
            
    start_dt = args.start_date
    end_dt = args.end_date
    
    if not end_dt:
        end_dt = ref_dt
    if not start_dt:
        if args.report == "daily":
            start_dt = end_dt
        elif args.report == "weekly":
            start_dt = end_dt - timedelta(days=6)
        else:
            start_dt = end_dt - timedelta(days=29)
            
    if start_dt > end_dt:
        print("Error: --start-date must be before or equal to --end-date.")
        return
        
    generate_report(args.report, start_dt, end_dt)

if __name__ == "__main__":
    main()

