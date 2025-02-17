SELECT 
    p.name,
    p.sku,
    p.category_id,
    c.name AS category_name,
    p.flavor_id,
    f.name AS flavor_name,
    p.size_id,
    s.name AS size_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN flavors f ON p.flavor_id = f.id
LEFT JOIN sizes s ON p.size_id = s.id
WHERE p.id = %s;
