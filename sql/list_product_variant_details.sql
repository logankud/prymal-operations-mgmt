SELECT 
    p.id AS product_id,
    p.name AS product_name,
    p.sku AS product_sku,
    p.price AS product_price,
    p.description AS product_description,
    p.created_at AS product_created_at,
    p.updated_at AS product_updated_at,
    c.name AS category_name,
    f.name as flavor_name,
    s.name as size_name
FROM 
    products p
LEFT JOIN 
    categories c ON p.category_id = c.id
LEFT JOIN 
    flavors f ON p.flavor_id = f.id
LEFT JOIN 
    sizes s ON p.flavor_id = s.id
ORDER BY 
    p.created_at DESC;
