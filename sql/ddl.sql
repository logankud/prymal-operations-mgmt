-- Create the `products` table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,                       -- Unique identifier for the product
    name VARCHAR(255) NOT NULL,                 -- Name of the product
    sku VARCHAR(100) UNIQUE NOT NULL,           -- Stock Keeping Unit for the product
    price DECIMAL(10, 2) CHECK (price >= 0) NOT NULL,  -- Price of the product in USD
    description TEXT,                           -- Detailed description of the product
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,  -- Links to the category of the product
    flavor_id INTEGER REFERENCES flavors(id) ON DELETE SET NULL,  -- Links to the flavor of the product
    size_id INTEGER REFERENCES sizes(id) ON DELETE SET NULL,  -- Links to the size of the product
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Timestamp when the record was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL  -- Timestamp of the last modification
);


-- Create the `categories` table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);



-- Create the `flavors` table
CREATE TABLE IF NOT EXISTS flavors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Create the `sizes` table
CREATE TABLE IF NOT EXISTS sizes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    weight_g INTEGER
);

-- Create the 'tags' table to manage tags on items 
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- Tag name must be unique
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS manufacturing_orders (
    id SERIAL PRIMARY KEY,                       
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE, 
    units_to_produce INTEGER NOT NULL CHECK (units_to_produce > 0),        
    planned_start_date DATE NOT NULL,              
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Complete')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,              
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL               
);

CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,                      -- Unique vendor identifier
    name VARCHAR(255) NOT NULL UNIQUE,          -- Vendor name (must be unique)
    email VARCHAR(255),                         -- Vendor email address (optional)
    address TEXT,                               -- Vendor address (optional)
    description TEXT,                           -- Brief description of the vendor (optional)
    notes TEXT,                                 -- Additional notes about the vendor (optional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL  -- Last update timestamp
);

CREATE TABLE IF NOT EXISTS unit_of_measure (
    id SERIAL PRIMARY KEY,                  -- Unique identifier for the unit
    name VARCHAR(100) NOT NULL UNIQUE,      -- Unit name (e.g., "kg", "liters", "grams")
    tag VARCHAR(10) NOT NULL UNIQUE,        -- Optional short form (e.g., "kg", "L", "g")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_materials (
    id SERIAL PRIMARY KEY,                      -- Unique identifier for the raw material
    name VARCHAR(255) NOT NULL,                 -- Raw material name
    vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE, -- Vendor reference
    unit_of_measure_id INTEGER NOT NULL REFERENCES unit_of_measure(id) ON DELETE CASCADE, -- Unit of measure reference
    moq FLOAT NOT NULL CHECK (moq >= 0),        -- Minimum Order Quantity
    tags JSONB DEFAULT '[]'::JSONB,             -- Array of tags stored as JSONB
    total_inventory FLOAT DEFAULT 0 CHECK (total_inventory >= 0), -- Total inventory on hand
    reserved_inventory FLOAT DEFAULT 0 CHECK (reserved_inventory >= 0), -- Reserved inventory (MO allocation)
    available_inventory FLOAT GENERATED ALWAYS AS (total_inventory - reserved_inventory) STORED, -- Available inventory
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL  -- Last update timestamp
);

CREATE TABLE IF NOT EXISTS bill_of_materials (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials(id) ON DELETE CASCADE,
    quantity_per_unit FLOAT NOT NULL CHECK (quantity_per_unit > 0)
);

CREATE TABLE IF NOT EXISTS stock_adjustments (
    id SERIAL PRIMARY KEY,                      -- Unique identifier for the stock adjustment
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials(id) ON DELETE CASCADE, -- Link to raw material
    adjustment_amount FLOAT NOT NULL,           -- The quantity adjusted (can be positive or negative)
    unit_of_measure VARCHAR(50) NOT NULL,       -- The unit of measure for the adjustment (matches raw material)
    reason TEXT NOT NULL,                       -- Reason for stock adjustment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL -- Timestamp when adjustment was made
);

CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_items (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials(id) ON DELETE CASCADE,
    quantity FLOAT NOT NULL CHECK (quantity > 0), -- Quantity required for the recipe
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_raw_materials (
    id SERIAL PRIMARY KEY,                   -- Unique identifier for the entry
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE, -- Links to recipes table
    raw_material_id INTEGER NOT NULL REFERENCES raw_materials(id) ON DELETE CASCADE, -- Links to raw materials table
    quantity FLOAT NOT NULL CHECK (quantity > 0), -- Quantity of raw material required
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, -- Timestamp for when the record is created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL  -- Timestamp for when the record is updated
);
