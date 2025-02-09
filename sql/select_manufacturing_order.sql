SELECT 
    id, 
    product_id, 
    size_id, 
    units_to_produce, 
    planned_start_date
FROM 
    manufacturing_orders
WHERE 
    id = %s;


