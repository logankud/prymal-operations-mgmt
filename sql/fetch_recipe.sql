SELECT 
    rm.name AS raw_material_name,
    rr.quantity AS quantity,
    um.tag AS unit,
    rm.total_inventory,
    rm.reserved_inventory,
    rm.available_inventory
FROM recipes r
JOIN recipe_raw_materials rr ON rr.recipe_id = r.id
JOIN raw_materials rm ON rm.id = rr.raw_material_id
JOIN unit_of_measure um ON um.id = rm.unit_of_measure_id
WHERE r.product_id = %s;
