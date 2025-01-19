-- Create the `products` table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,                       -- Unique identifier for the product
    name VARCHAR(255) NOT NULL,                 -- Name of the product
    sku VARCHAR(100) UNIQUE NOT NULL,           -- Stock Keeping Unit for the product
    price DECIMAL(10, 2) CHECK (price >= 0) NOT NULL,  -- Price of the product in USD
    description TEXT,                           -- Detailed description of the product
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,  -- Links to the category of the product
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

-- -- Create the `product_variants` table
-- CREATE TABLE IF NOT EXISTS product_variants (
--     id SERIAL PRIMARY KEY,
--     product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
--     flavor_id INTEGER REFERENCES flavors(id),
--     size_id INTEGER REFERENCES sizes(id),
--     price DECIMAL(10,2) CHECK (price >= 0) NOT NULL,
--     is_active BOOLEAN DEFAULT TRUE
-- );

-- -- Create the `product_types` table
-- CREATE TABLE IF NOT EXISTS product_types (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100) UNIQUE NOT NULL
-- );
