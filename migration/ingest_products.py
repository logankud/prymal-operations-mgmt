import pandas as pd
import psycopg2
import sys

sys.path.append('')  # Adding root of the repo to path for importing modules
from utils import get_db_connection

# Path to the CSV file
CSV_FILE_PATH = "migration/data/ProductCatalogExport_20250216.csv"

# Read the CSV file
df = pd.read_csv(CSV_FILE_PATH)
print(df.head())  # Debugging: Show first few rows

# Ensure 'On Hand Quantity' exists in the CSV
if "On Hand Quantity" not in df.columns:
    raise KeyError("Missing required column: 'On Hand Quantity' in CSV file.")

# Connect to the database
conn = get_db_connection()
cur = conn.cursor()

# 🛠 Insert products into the database
for index, row in df.iterrows():
    product_sku = str(row["Product Id"]).strip()  # Convert to string for uniformity
    product_name = row["Product Name"].strip()
    on_hand_quantity = row["On Hand Quantity"]

    # Skip records where On Hand Quantity is <= 0
    if on_hand_quantity <= 0:
        print(f'Skipping Product: SKU={product_sku}, Name={product_name} (On Hand={on_hand_quantity})')
        continue

    print(f'Processing Product: SKU={product_sku}, Name={product_name}, On Hand={on_hand_quantity}')

    # Check if product already exists
    cur.execute("SELECT id FROM products WHERE sku = %s;", (product_sku,))
    existing_product = cur.fetchone()

    if existing_product:
        print(f'Product {product_sku} already exists. Skipping insert.')
    else:
        print(f'Inserting new product: {product_name}')

        # Insert new product
        insert_query = """
            INSERT INTO products (sku, name, price, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW());
        """
        cur.execute(insert_query, (product_sku, product_name, 0.00))  # Default price is 0 for now
        print("Insert successful")

# Commit changes & Close connection
conn.commit()
cur.close()
conn.close()

print("Products imported successfully!")
