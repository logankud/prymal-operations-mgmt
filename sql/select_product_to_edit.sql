SELECT 
    p.id AS product_id,
    p.name AS product_name,
    p.sku AS product_sku,
    p.price AS product_price,
    p.description AS product_description,
    p.category_id AS product_category_id
FROM 
    products p
WHERE 
    p.id = %s;
