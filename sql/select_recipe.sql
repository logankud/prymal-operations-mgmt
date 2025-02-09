SELECT 
    r.id, p.name AS product_name, r.created_at, r.updated_at
FROM 
    recipes r
JOIN 
    products p ON r.product_id = p.id
WHERE 
    r.id = %s;
