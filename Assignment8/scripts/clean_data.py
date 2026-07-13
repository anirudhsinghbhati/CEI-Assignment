import os
import pandas as pd
from datetime import datetime

RAW_DIR = os.path.join("data", "raw")
CLEAN_DIR = os.path.join("data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)
REPORT_PATH = os.path.join(CLEAN_DIR, "cleaning_report.txt")


CUSTOMERS_RAW = os.path.join(RAW_DIR, "customers.csv")
PRODUCTS_RAW = os.path.join(RAW_DIR, "products.csv")
ORDERS_RAW = os.path.join(RAW_DIR, "orders.csv")
ORDER_ITEMS_RAW = os.path.join(RAW_DIR, "order_items.csv")

CUSTOMERS_CLEAN = os.path.join(CLEAN_DIR, "customers_clean.csv")
PRODUCTS_CLEAN = os.path.join(CLEAN_DIR, "products_clean.csv")
ORDERS_CLEAN = os.path.join(CLEAN_DIR, "orders_clean.csv")
ORDER_ITEMS_CLEAN = os.path.join(CLEAN_DIR, "order_items_clean.csv")


issues_report = {
    "null_customer_ids_removed": 0,
    "invalid_emails_found": [],
    "orphaned_order_items_removed": 0,
    "duplicate_records_removed": {},
    "invalid_dates_fixed": 0,
    "invalid_discount_percent_removed": 0,
    "zero_quantity_items_removed": 0,
    "future_date_orders_removed": 0
}

def clean_orders(orders_df):
    initial_count = len(orders_df)
    
    # Drop duplicates
    orders_df = orders_df.drop_duplicates(subset=["order_id"])
    dup_removed = initial_count - len(orders_df)
    issues_report["duplicate_records_removed"]["orders"] = dup_removed

    #  Handle NULL/empty customer_ids

    null_cust_mask = orders_df["customer_id"].isna() | (orders_df["customer_id"].astype(str).str.strip() == "")
    null_cust_count = null_cust_mask.sum()
    issues_report["null_customer_ids_removed"] = int(null_cust_count)
    orders_df = orders_df[~null_cust_mask].copy()

    #  Fix date formats
    def parse_order_date(val):
        if pd.isna(val):
            return pd.NaT
        val_str = str(val).strip()
    
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y"):
            try:
                return pd.to_datetime(val_str, format=fmt)
            except (ValueError, TypeError):
                continue
       
        try:
            return pd.to_datetime(val_str)
        except Exception:
            return pd.NaT

    original_dates = orders_df["order_date"].copy()
    parsed_dates = orders_df["order_date"].apply(parse_order_date)
    orders_df["order_date"] = parsed_dates
    
    wrong_format_count = 0
    for orig, parsed in zip(original_dates, parsed_dates):
        if pd.notna(orig) and pd.notna(parsed):
           
            orig_str = str(orig).strip()
            if len(orig_str) == 10 and orig_str[2] == '-' and orig_str[5] == '-':
                wrong_format_count += 1
                
    issues_report["invalid_dates_fixed"] = int(wrong_format_count)
    

    reference_date = datetime(2026, 7, 9, 23, 59, 59)
    future_dates_mask = orders_df["order_date"] > reference_date
    future_dates_count = future_dates_mask.sum()
    issues_report["future_date_orders_removed"] = int(future_dates_count)
    orders_df = orders_df[~future_dates_mask].copy()

    # Change order date to  string format
    orders_df["order_date"] = orders_df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    return orders_df

def clean_products(products_df):
   
    initial_count = len(products_df)
    products_df = products_df.drop_duplicates(subset=["product_id"])
    dup_removed = initial_count - len(products_df)
    issues_report["duplicate_records_removed"]["products"] = dup_removed


    products_df["product_name"] = products_df["product_name"].astype(str).str.strip().str.title()
    
  
    products_df["category"] = products_df["category"].astype(str).str.strip()
    products_df["subcategory"] = products_df["subcategory"].astype(str).str.strip()
    
    return products_df

def validate_emails(customers_df):
    
    invalid_cust_ids = []
    for idx, row in customers_df.iterrows():
        cust_id = row["customer_id"]
        email = str(row["email"]).strip()
        
        # email validation
        if not email or "@" not in email:
            invalid_cust_ids.append(cust_id)
            continue
        
        parts = email.split("@")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            invalid_cust_ids.append(cust_id)
            continue
            
        domain_parts = parts[1].split(".")
        if len(domain_parts) < 2 or not all(domain_parts):
            invalid_cust_ids.append(cust_id)
            
    issues_report["invalid_emails_found"] = invalid_cust_ids
    return invalid_cust_ids

def check_referential_integrity(order_items_df, orders_df, products_df):
   
    # Check invalid orders
    valid_orders = set(orders_df["order_id"])
    orphaned_orders_mask = ~order_items_df["order_id"].isin(valid_orders)
    orphaned_orders_count = orphaned_orders_mask.sum()
    
    # Check invalid products
    valid_products = set(products_df["product_id"])
    orphaned_products_mask = ~order_items_df["product_id"].isin(valid_products)
    orphaned_products_count = orphaned_products_mask.sum()
    
    total_orphaned = orphaned_orders_count + orphaned_products_count
    issues_report["orphaned_order_items_removed"] = int(total_orphaned)
    
    # Drop orphaned order items
    clean_items_df = order_items_df[~orphaned_orders_mask & ~orphaned_products_mask].copy()
    
    return clean_items_df

def run_cleaning_pipeline():
    # Load all raw files
    cust_df = pd.read_csv(CUSTOMERS_RAW)
    prod_df = pd.read_csv(PRODUCTS_RAW)
    ord_df = pd.read_csv(ORDERS_RAW)
    item_df = pd.read_csv(ORDER_ITEMS_RAW)
    
    # Clean customers
    initial_cust_count = len(cust_df)
    cust_df = cust_df.drop_duplicates(subset=["customer_id"])
    issues_report["duplicate_records_removed"]["customers"] = initial_cust_count - len(cust_df)
    
    # Validate emails
    invalid_emails = validate_emails(cust_df)
    
    # Clean products
    prod_clean = clean_products(prod_df)
    
    # Clean orders
    ord_clean = clean_orders(ord_df)
    
    # Check referential integrity on order items
    initial_items_count = len(item_df)
    item_df = item_df.drop_duplicates(subset=["item_id"])
    issues_report["duplicate_records_removed"]["order_items"] = initial_items_count - len(item_df)
    
    # Validate order item values (e.g. quantity = 0, discount_percent > 100)
    # discount_percent > 100 or < 0
    invalid_discount_mask = (item_df["discount_percent"] > 100.0) | (item_df["discount_percent"] < 0.0)
    issues_report["invalid_discount_percent_removed"] = int(invalid_discount_mask.sum())
    item_df = item_df[~invalid_discount_mask]
    
    #  quantity = 0
    zero_qty_mask = item_df["quantity"] == 0
    issues_report["zero_quantity_items_removed"] = int(zero_qty_mask.sum())
    item_df = item_df[~zero_qty_mask]
    
    # Clean and perform integrity check
    item_clean = check_referential_integrity(item_df, ord_clean, prod_clean)
    
    # Export cleaned CSVs
    cust_df.to_csv(CUSTOMERS_CLEAN, index=False)
    prod_clean.to_csv(PRODUCTS_CLEAN, index=False)
    ord_clean.to_csv(ORDERS_CLEAN, index=False)
    item_clean.to_csv(ORDER_ITEMS_CLEAN, index=False)
    
    # Write report file
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("=" * 60 + "\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("1. Duplicates Removed:\n")
        for table, val in issues_report["duplicate_records_removed"].items():
            f.write(f"   - {table}: {val} duplicates\n")
            
        f.write(f"\n2. Orders NULL Customer IDs Removed: {issues_report['null_customer_ids_removed']}\n")
        f.write(f"3. Orders Date Formats Fixed: {issues_report['invalid_dates_fixed']}\n")
        f.write(f"4. Orders Future Date Removed: {issues_report['future_date_orders_removed']}\n")
        f.write(f"5. Order Items Orphans Removed: {issues_report['orphaned_order_items_removed']}\n")
        f.write(f"6. Order Items Invalid Discounts Removed: {issues_report['invalid_discount_percent_removed']}\n")
        f.write(f"7. Order Items Zero Quantities Removed: {issues_report['zero_quantity_items_removed']}\n")
        
        f.write(f"\n8. Invalid Emails Found (Count: {len(invalid_emails)}):\n")
        if invalid_emails:
            for c_id in invalid_emails:
                cust_name = cust_df.loc[cust_df["customer_id"] == c_id, "customer_name"].values[0]
                cust_email = cust_df.loc[cust_df["customer_id"] == c_id, "email"].values[0]
                f.write(f"   - Customer ID: {c_id} | Name: {cust_name} | Email: {cust_email}\n")
        else:
            f.write("   - None\n")
            
        f.write("\nSummary of Exported Clean Datasets:\n")
        f.write(f"   - customers_clean.csv: {len(cust_df)} rows\n")
        f.write(f"   - products_clean.csv: {len(prod_clean)} rows\n")
        f.write(f"   - orders_clean.csv: {len(ord_clean)} rows\n")
        f.write(f"   - order_items_clean.csv: {len(item_clean)} rows\n")
        f.write("=" * 60 + "\n")
        
    print("Data cleaning pipeline execution completed successfully!")
    print(f"Cleaned datasets exported to '{CLEAN_DIR}' directory.")
    

if __name__ == "__main__":
    run_cleaning_pipeline()
