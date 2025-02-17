SELECT 
    ps.id, 
    p.name, 
    p.sku, 
    c.name AS category, 
    f.name AS flavor, 
    s.name AS size, 
    p.price, 
    ps.created_at 
FROM product_snapshots ps
JOIN products p ON ps.product_id = p.id
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN flavors f ON p.flavor_id = f.id
LEFT JOIN sizes s ON p.size_id = s.id
WHERE ps.id = %s;
