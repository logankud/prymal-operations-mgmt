import pandas as pd
import psycopg2
import sys

sys.path.append('')  # Adding root of the repo to path for importing modules
from utils import get_db_connection

# Path to the CSV file
CSV_FILE_PATH = "migration/data/ProductRecipes-2025-02-15-19_48.csv"

# Read the CSV file
df = pd.read_csv(CSV_FILE_PATH)
print(df.head())  # Debugging: Show first few rows

# Remove records missing "Product variant code / SKU (required)" 
df = df[df["Product variant code / SKU (required)"].notna()].copy()

# Ensure required columns exist in the CSV
required_columns = [
    "Product variant code / SKU (required)",
    "Ingredient variant name",
    "Quantity (required)",
    "Unit of measure"
]
for col in required_columns:
    if col not in df.columns:
        raise KeyError(f"Missing required column: '{col}' in CSV file.")

# Convert SKU column to string to ensure consistency with DB
df["Product variant code / SKU (required)"] = df["Product variant code / SKU (required)"].astype(str)

# Connect to the database
conn = get_db_connection()
cur = conn.cursor()

# Iterate through products to insert recipes and raw materials
for product_sku, product_data in df.groupby("Product variant code / SKU (required)"):

    product_sku = str(product_sku).split('.')[0]

    print(f'Processing Product SKU: {product_sku}')

    # Query the database for the product ID
    cur.execute("SELECT id FROM products WHERE sku = %s;", (product_sku,))
    product_id_result = cur.fetchone()

    print(product_id_result)

    if not product_id_result:
        print(f"Skipping SKU {product_sku}, product not found in database.")
        continue

    product_id = product_id_result[0]  # Extract the ID from the tuple
    print(f"Found Product ID: {product_id} for SKU: {product_sku}")

    # Insert a new recipe version
    insert_recipe_query = """
        INSERT INTO recipes (product_id, active, created_at)
        VALUES (%s, FALSE, NOW()) RETURNING id;
    """
    cur.execute(insert_recipe_query, (product_id,))
    recipe_id = cur.fetchone()[0]

    # Insert raw materials for this recipe
    for _, row in product_data.iterrows():
        raw_material_name = row["Ingredient variant name"].strip().lower()

        # Query the database for the raw material ID
        cur.execute("SELECT id FROM raw_materials WHERE LOWER(name) = %s;", (raw_material_name,))
        raw_material_result = cur.fetchone()

        if not raw_material_result:
            print(f"Skipping raw material '{row['Ingredient variant name']}', not found in database.")
            continue

        raw_material_id = raw_material_result[0]  # Extract the ID from the tuple
        quantity = row["Quantity (required)"]

        insert_ingredient_query = """
            INSERT INTO recipe_raw_materials (recipe_id, raw_material_id, quantity, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW());
        """
        cur.execute(insert_ingredient_query, (recipe_id, raw_material_id, quantity))

    print(f"Recipe imported for SKU: {product_sku}")

# Commit changes & Close connection
conn.commit()
cur.close()
conn.close()

print("Product recipes imported successfully!")
