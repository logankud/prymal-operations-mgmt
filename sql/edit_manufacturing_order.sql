UPDATE manufacturing_orders
SET 
    product_id = %s, 
    size_id = %s, 
    units_to_produce = %s, 
    planned_start_date = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE 
    id = %s;
