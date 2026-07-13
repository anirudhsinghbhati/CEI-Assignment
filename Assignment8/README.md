# E-Commerce Order Analytics System

## Overview

This project is an end-to-end E-Commerce Order Analytics System built using Python, Pandas, SQLite, and SQL.

The system generates realistic e-commerce datasets, introduces common data quality issues, cleans and validates the data, loads it into a relational database, performs business analytics using SQL, and provides reports through a command-line interface (CLI).

---

## Project Workflow

1. Generate raw e-commerce datasets
2. Introduce intentional data quality issues
3. Clean and validate data using Pandas
4. Load cleaned data into SQLite
5. Perform SQL analytics and reporting
6. Run cohort, retention, and customer segmentation analysis
7. Generate reports through a CLI tool

---

## Project Structure

```text
ecommerce-analytics-system/
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   │
│   └── cleaned/
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── db_setup.py
│   ├── report_cli.py
│   └── test_edge_cases.py
│
├── sql/
│   ├── schema.sql
│   ├── aggregations.sql
│   ├── window_functions.sql
│   └── cohort_analysis.sql
│
├── output/
│   └── sample_reports/
│
├── ecommerce.db
└── README.md
└── Report.pdf ( Summary + Screenshots)
```

---

## Dataset Generation

The dataset generation script creates four related tables:

* Customers
* Products
* Orders
* Order Items

Intentional inconsistencies are added to simulate real-world data problems:

* Duplicate records
* Missing customer IDs
* Invalid email formats
* Wrong date formats
* Future order dates
* Orphan order items
* Invalid discount values
* Zero quantity records

Run:

```bash
python scripts/generate_data.py
```

---

## Data Cleaning

The cleaning pipeline is implemented using Pandas.

### Cleaning Operations

* Remove duplicate records
* Remove orders with missing customer IDs
* Standardize date formats
* Remove future-dated orders
* Validate email addresses
* Remove orphan order items
* Remove invalid discount percentages
* Remove zero quantity records

Run:

```bash
python scripts/clean_data.py
```

After execution, cleaned files are generated inside:

```text
data/cleaned/
```

A cleaning report is also generated:

```text
data/cleaned/cleaning_report.txt
```

---

## Database Setup

SQLite is used as the database.

The schema includes:

* Primary Keys
* Foreign Keys
* NOT NULL Constraints
* CHECK Constraints

Run:

```bash
python scripts/db_setup.py
```

This script:

* Creates all tables
* Loads cleaned CSV files
* Verifies row counts
* Checks referential integrity

---

## SQL Analytics

The project includes multiple analytical SQL queries.

### Aggregation Analysis

* Revenue by category
* Top customers by spending
* Monthly order trends
* Return analysis
* Customer order behavior

### Window Functions & CTEs

* Customer ranking by revenue
* Running totals
* Moving averages
* Revenue growth calculations
* Customer segmentation

### Cohort & Retention Analysis

* Customer cohorts by first purchase month
* Monthly retention rates
* Repeat customer analysis

SQL files are stored in:

```text
sql/
```

---

## Edge Case Testing

Unit tests are included to verify important data quality scenarios.

Covered cases:

* Orphan order items
* Invalid discount percentages
* Zero quantity records
* Future order dates

Run:

```bash
python scripts/test_edge_cases.py
```

---

## CLI Reporting Tool

The project includes a command-line reporting tool that reads data directly from SQLite and generates reports.

### Usage

```bash
python scripts/report_cli.py
```

### Period Summary Reports (PDF requirements)

* **Weekly Report**:
  ```bash
  python scripts/report_cli.py --report weekly
  ```
* **Daily Report**:
  ```bash
  python scripts/report_cli.py --report daily
  ```
* **Custom Date Range**:
  ```bash
  python scripts/report_cli.py --report daily --start-date 2026-06-01 --end-date 2026-06-05
  ```

### Analytical Reports (Text requirements)

* **Revenue Analytics Report**:
  (Shows revenue by product category, and customer-wise, category-wise monthly revenue breakdown)
  ```bash
  python scripts/report_cli.py --report revenue
  ```

* **Top Customers & Spend Rankings**:
  (Shows top customers by spending, and ranks all customers by lifetime value using DENSE_RANK)
  ```bash
  python scripts/report_cli.py --report top_customers
  ```

* **Cohort Retention Analysis**:
  (Shows monthly retention rates grouped by both registration month and first purchase month cohorts)
  ```bash
  python scripts/report_cli.py --report retention
  ```

* **Customer Segmentation & RFM**:
  (Shows Average Order Value (AOV) by frequency segment, and outputs full Recency, Frequency, Monetary summary segments)
  ```bash
  python scripts/report_cli.py --report segmentation
  ```

---

## Example Report Metrics

The CLI tool displays:

* Total Orders, Revenue, and Unique Customers (with period-over-period % change)
* Top Products by Quantity and Revenue
* Daily / Weekly / Monthly Breakdown
* Customer Spend & LTV Rankings
* Registration vs First Purchase Cohort Retention Tables
* RFM Segments and AOV by segments

---

## Technologies Used

* Python
* Pandas
* SQLite
* SQL
* argparse
* unittest

---

## Key Concepts Demonstrated

* Data Generation
* Data Cleaning
* Data Validation
* Referential Integrity
* SQL Joins
* Aggregations
* Window Functions
* CTEs
* Cohort Analysis
* Retention Analysis
* Customer Segmentation
* CLI Development

---

## Conclusion

This project demonstrates a complete data analytics workflow starting from raw data generation to business reporting. It combines Python-based data engineering tasks with SQL analytics and provides a practical example of handling real-world e-commerce data.
