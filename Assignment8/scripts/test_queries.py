import sqlite3
import os

DB_PATH = "ecommerce.db"
SQL_FILES = [
    os.path.join("sql", "aggregations.sql"),
    os.path.join("sql", "window_functions.sql"),
    os.path.join("sql", "cohort_analysis.sql")
]

def run_test():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at '{DB_PATH}'")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    for sql_file in SQL_FILES:
        print("\n" + "=" * 60)
        print(f"Executing queries from: {sql_file}")
        print("=" * 60)
        
        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read()
            
       
       
        statements = content.split(";")
        
        query_idx = 1
        for stmt in statements:
            stmt_clean = stmt.strip()

            if not stmt_clean or stmt_clean.startswith("--") and len(stmt_clean.split("\n")) <= 1:
                continue
                
            
            lines = [l.strip() for l in stmt_clean.split("\n")]
            non_comment_lines = [l for l in lines if l and not l.startswith("--")]
            if not non_comment_lines:
                continue
                
           
            comment_header = ""
            for line in lines:
                if line.startswith("--"):
                    comment_header += line + "\n"
                else:
                    break
                    
            print(f"\nQuery #{query_idx}:")
            if comment_header:
                print(comment_header.strip())
                
            try:
                cursor.execute(stmt_clean)
                col_names = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                
                print(f"Columns: {col_names}")
                print(f"Returned {len(rows)} rows. First 3 rows:")
                for r in rows[:3]:
                    print(f"  {r}")
            except Exception as e:
                print(f"ERROR executing query: {e}")
                print(f"Statement:\n{stmt_clean}")
                
            query_idx += 1
            
    conn.close()
    print("\nAll queries executed.")

if __name__ == "__main__":
    run_test()
