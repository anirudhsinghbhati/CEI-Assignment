import csv
import random
import os
from datetime import datetime, timedelta


random.seed(42)


NUM_CUSTOMERS = 600
NUM_PRODUCTS = 500
NUM_ORDERS = 800 
RAW_DIR = os.path.join("data", "raw")

os.makedirs(RAW_DIR, exist_ok=True)


FIRST_NAMES = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia", "Kevin", "Laura", "Michael", "Sarah", "David", "Emma", "James", "Olivia"]
LAST_NAMES = ["Smith", "Doe", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Davis", "White", "Clark", "Hall", "Thomas", "Martin", "Garcia", "Roy", "Lee", "Harris", "Lewis", "Clark", "Robinson"]
DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
REGIONS = ["US-EAST", "US-WEST", "EU-WEST", "APAC-EAST", "LATAM-SOUTH"]
STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet", "Camera"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Socks", "Sweater"],
    "Home": ["Lamp", "Chair", "Table", "Rug", "Blender", "Cookware"],
    "Books": ["Fiction", "Non-Fiction", "Sci-Fi", "Biography", "Mystery", "History"]
}

# Generate Customers
customers = []
customer_ids = [f"CUST{i:05d}" for i in range(1, NUM_CUSTOMERS + 1)]

start_reg = datetime(2025, 1, 1)
end_reg = datetime(2026, 5, 1)
reg_days_range = (end_reg - start_reg).days

for cust_id in customer_ids:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    
    
    rand_val = random.random()
    if rand_val < 0.01:
      
        email = f"{first.lower()}.{last.lower()}{random.randint(10,99)}{random.choice(DOMAINS)}"
    elif rand_val < 0.02:
       
        email = f"{first.lower()}.{last.lower()}{random.randint(10,99)}@"
    else:
        email = f"{first.lower()}.{last.lower()}{random.randint(10,99)}@{random.choice(DOMAINS)}"
        
    reg_date = start_reg + timedelta(days=random.randint(0, reg_days_range), seconds=random.randint(0, 86399))
    cust_type = random.choice(CUSTOMER_TYPES)
    
    customers.append({
        "customer_id": cust_id,
        "customer_name": name,
        "email": email,
        "registration_date": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_type": cust_type
    })

# Write Customers CSV
customers_file = os.path.join(RAW_DIR, "customers.csv")
with open(customers_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["customer_id", "customer_name", "email", "registration_date", "customer_type"])
    writer.writeheader()
    writer.writerows(customers)


# Generate Products
products = []
product_ids = [f"PROD{i:05d}" for i in range(1, NUM_PRODUCTS + 1)]

for prod_id in product_ids:
    category = random.choice(list(CATEGORIES.keys()))
    subcategory = random.choice(CATEGORIES[category])
    

    raw_name = f"{subcategory} {random.randint(100, 999)}"
    if random.random() < 0.10:

        spaces_before = " " * random.randint(1, 3)
        spaces_after = " " * random.randint(1, 3)
        if random.random() < 0.5:
            
            raw_name = "".join(c.upper() if random.random() < 0.5 else c.lower() for c in raw_name)
        product_name = f"{spaces_before}{raw_name}{spaces_after}"
    else:
        product_name = raw_name
        
    cost_price = round(random.uniform(5.0, 500.0), 2)
    
    products.append({
        "product_id": prod_id,
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "cost_price": cost_price
    })

# Write Products CSV
products_file = os.path.join(RAW_DIR, "products.csv")
with open(products_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "subcategory", "cost_price"])
    writer.writeheader()
    writer.writerows(products)


# Generate Orders
orders = []
order_ids = [f"ORD{i:05d}" for i in range(1, NUM_ORDERS + 1)]


for idx, ord_id in enumerate(order_ids):
  
    cust = random.choice(customers)
    cust_id = cust["customer_id"]
    
  
    if random.random() < 0.05:
        cust_id = ""
        
    
    if cust_id:
        reg_dt = datetime.strptime(cust["registration_date"], "%Y-%m-%d %H:%M:%S")
    else:
        reg_dt = start_reg
        
  
    end_orders = datetime(2026, 6, 30)
    if reg_dt < end_orders:
        days_diff = (end_orders - reg_dt).days
        order_dt = reg_dt + timedelta(days=random.randint(0, max(0, days_diff)), seconds=random.randint(0, 86399))
    else:
        order_dt = reg_dt
        
    status = random.choice(STATUSES)
    region_code = random.choice(REGIONS)
    
    
    if random.random() < 0.08:
    
        order_date_str = order_dt.strftime("%d-%m-%Y")
    else:

        order_date_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")
        
    orders.append({
        "order_id": ord_id,
        "customer_id": cust_id,
        "order_date": order_date_str,
        "status": status,
        "region_code": region_code
    })

# Write Orders CSV
orders_file = os.path.join(RAW_DIR, "orders.csv")
with open(orders_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date", "status", "region_code"])
    writer.writeheader()
    writer.writerows(orders)


#  Generate Order Items
order_items = []
item_counter = 1

for ord_rec in orders:
    ord_id = ord_rec["order_id"]

    num_items = random.randint(1, 4)
    

    seen_products = set()
    
    for _ in range(num_items):
        item_id = f"ITEM{item_counter:06d}"
        
      
        prod = random.choice(products)
        prod_id = prod["product_id"]
        while prod_id in seen_products:
            prod = random.choice(products)
            prod_id = prod["product_id"]
        seen_products.add(prod_id)
        
       
        markup = round(random.uniform(1.1, 1.5), 2)
        unit_price = round(prod["cost_price"] * markup, 2)
        
       
        quantity = random.randint(1, 8)
        
        
        if random.random() < 0.03:
            quantity = -quantity
            
        
        discount_choice = random.random()
        if discount_choice < 0.60:
            discount_percent = 0.0
        elif discount_choice < 0.90:
            discount_percent = float(random.choice([5, 10, 15, 20, 25, 30]))
        else:
            discount_percent = float(random.choice([40, 50]))
            
        order_items.append({
            "item_id": item_id,
            "order_id": ord_id,
            "product_id": prod_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent
        })
        item_counter += 1

# Add some orphaned order items to verify referential integrity checks 
for _ in range(10):
    item_id = f"ITEM{item_counter:06d}"
    non_existent_ord_id = f"ORD{random.randint(9000, 9999):05d}"
    prod = random.choice(products)
    prod_id = prod["product_id"]
    quantity = random.randint(1, 5)
    unit_price = round(prod["cost_price"] * 1.3, 2)
    discount_percent = 0.0
    
    order_items.append({
        "item_id": item_id,
        "order_id": non_existent_ord_id,
        "product_id": prod_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_percent": discount_percent
    })
    item_counter += 1

# Write Order Items CSV
order_items_file = os.path.join(RAW_DIR, "order_items.csv")
with open(order_items_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])
    writer.writeheader()
    writer.writerows(order_items)

print(f"Data generation complete! Exported raw CSVs to '{RAW_DIR}':")
print(f"  - customers.csv: {len(customers)} rows")
print(f"  - products.csv: {len(products)} rows")
print(f"  - orders.csv: {len(orders)} rows")
print(f"  - order_items.csv: {len(order_items)} rows")
