SELECT 
    p.id, 
    p.name, 
    p.sku, 
    p.price, 
    p.description, 
    c.name AS category_name,  -- Get category name instead of ID
    f.name AS flavor_name,    -- Get flavor name instead of ID
    s.name AS size_name,      -- Get size name instead of ID
    p.created_at, 
    p.updated_at
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN flavors f ON p.flavor_id = f.id
LEFT JOIN sizes s ON p.size_id = s.id
WHERE p.id = %s;
