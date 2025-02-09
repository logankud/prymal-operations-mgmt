SELECT 
    mo.id, 
    p.name AS product_name, 
    mo.units_to_produce,
    mo.planned_start_date, 
    mo.created_at, 
    mo.updated_at
FROM 
    manufacturing_orders mo
JOIN 
    products p ON mo.product_id = p.id
ORDER BY 
    mo.planned_start_date;
