import pandas as pd
import numpy as np
import psycopg2
import sys

sys.path.append('')  # adding root of the repo to path for importing modules
from utils import get_db_connection

# Path to the CSV file
CSV_FILE_PATH = "migration/data/InventoryItems-2025-02-16-11_55 - InventoryItems-2025-02-16-11_55.csv"

# Read the CSV file
df = pd.read_csv(CSV_FILE_PATH)
print(df.head())

# Database connection
conn = get_db_connection()
cur = conn.cursor()

# Function to get vendor ID
def get_vendor_id(vendor_name):
    print(f'Vendor Name: {vendor_name}')
    cur.execute("SELECT id FROM vendors WHERE name = %s;", (vendor_name,))
    result = cur.fetchone()
    print(result[0])
    return result[0] if result else None

# Function to get unit_of_measure ID
def get_unit_of_measure_id(unit_name):
    print(f'UOM: {unit_name}')
    cur.execute("SELECT id FROM unit_of_measure WHERE name = %s;", (unit_name,))
    result = cur.fetchone()
    print(result[0])
    return result[0] if result else None

# Insert raw materials
for index, row in df.iterrows():
    print(f'Inserting raw material: {row["Name"]}')
    name = row["Name"]
    # Convert NaN values to None
    vendor_name = None if pd.isna(row["Default supplier"]) else row["Default supplier"]
    unit_name = None if pd.isna(row["Units of measure"]) else row["Units of measure"]

    print(f'Vendor Name: {vendor_name}')  # Debugging
    print(f'Unit Name: {unit_name}')      # Debugging

    total_inventory = row["In stock"]
    reserved_inventory = row["Committed"]
    available_inventory = row["Calculated stock"]


    print(f'Vendor is np.NaN: {vendor_name == np.nan}')
    print(f'Vendor is str NAN: {vendor_name == "NaN"}')
    print(type(vendor_name))
    

    # Ensure both vendor and unit exist before inserting
    if vendor_name and unit_name:

        # Get vendor ID and unit ID
        vendor_id = get_vendor_id(vendor_name)
        unit_id = get_unit_of_measure_id(unit_name)

        # Ensure both vendor and unit exist before inserting
        if vendor_id and unit_id:
            print(f'Vendor ID: {vendor_id}, Unit ID: {unit_id}')
            
            # Check if raw material already exists
            cur.execute("SELECT id FROM raw_materials WHERE name = %s;", (name,))
            existing_record = cur.fetchone()
    
            if existing_record is not None:
                print(f'Raw material {name} already exists. Updating inventory levels')
                # Update inventory if raw material exists
                update_query = """
                    UPDATE raw_materials
                    SET total_inventory = %s, reserved_inventory = %s
                    WHERE id = %s;
                """
                cur.execute(update_query, (total_inventory, reserved_inventory, existing_record[0]))
            else:
                print(f'Raw material {name} does not exist. Inserting new record')
    
                # Insert new raw material
                insert_query = """
                    INSERT INTO raw_materials (name, vendor_id, unit_of_measure_id, total_inventory, reserved_inventory)
                    VALUES (%s, %s, %s, %s, %s);
                """
                cur.execute(insert_query, (name, vendor_id, unit_id, total_inventory, reserved_inventory))
                print("Insert successful")
    
    
                conn.commit()

        else:
            print(f"Skipping {name} - Vendor or Unit of Measure missing.")

    else:
        print(f"Skipping {name} - Vendor or Unit of Measure missing.")

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()

print("Raw materials imported successfully!")
