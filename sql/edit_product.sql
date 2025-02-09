UPDATE products
SET name = %s, 
    sku = %s, 
    price = %s, 
    description = %s, 
    category_id = %s, 
    flavor_id = %s, 
    size_id = %s, 
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s;
