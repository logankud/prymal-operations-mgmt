SELECT 
    id, 
    created_at 
FROM product_snapshots 
WHERE product_id = %s
ORDER BY created_at DESC;
