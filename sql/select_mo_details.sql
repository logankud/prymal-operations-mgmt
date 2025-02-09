SELECT product_id, units_to_produce, status 
FROM manufacturing_orders 
WHERE id = %s;
