import sqlite3
import pandas as pd
import os

DB_PATH = "ecommerce.db"
SCHEMA_SQL = os.path.join("sql", "schema.sql")
CLEAN_DIR = os.path.join("data", "cleaned")

def setup_database():
    # 1. Connect to SQLite 
    print(f"Connecting to database at '{DB_PATH}'...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Read and run schema.sql
    print(f"Initializing schema from '{SCHEMA_SQL}'...")
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        schema_query = f.read()
    
    # handles multiple SQL statements 
    cursor.executescript(schema_query)
    conn.commit()
    print("Schema initialized successfully.")
    
    # 3. Load cleaned CSVs into tables
    tables_to_load = {
        "customers": "customers_clean.csv",
        "products": "products_clean.csv",
        "orders": "orders_clean.csv",
        "order_items": "order_items_clean.csv"
    }
    
    for table_name, csv_file in tables_to_load.items():
        csv_path = os.path.join(CLEAN_DIR, csv_file)
        if not os.path.exists(csv_path):
            print(f"Error: Cleaned file not found at '{csv_path}'")
            continue
            
        print(f"Loading '{csv_file}' into table '{table_name}'...")
        df = pd.read_csv(csv_path)
        
        # Write to SQLite
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()
        
    # 4. Verify Row Counts and Foreign Key Constraints
    print("\nVerifying loaded row counts:")
    for table_name in tables_to_load.keys():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - Table '{table_name}': {count} rows loaded")
        
    # Check if there are any foreign key violations
    cursor.execute("PRAGMA foreign_key_check;")
    violations = cursor.fetchall()
    if violations:
        print("\nWARNING: Foreign key violations detected!")
        for v in violations:
            print(f"   - Table: {v[0]}, RowId: {v[1]}, Target: {v[2]}, FkId: {v[3]}")
    else:
        print("\nReferential integrity check passed: No foreign key violations in SQLite database.")
        
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
