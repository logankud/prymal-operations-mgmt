SELECT 
    rr.raw_material_id,
    rm.name AS raw_material_name,
    rr.quantity,
    uom.name AS unit,
    rm.total_inventory,
    rm.reserved_inventory,
    rm.available_inventory
FROM 
    recipe_raw_materials rr
JOIN 
    recipes r ON rr.recipe_id = r.id
JOIN 
    raw_materials rm ON rr.raw_material_id = rm.id
JOIN 
    unit_of_measure uom ON rm.unit_of_measure_id = uom.id
WHERE 
    r.product_id = %s
    AND r.active = TRUE  -- Ensures we only get the active recipe
ORDER BY 
    rm.name;
