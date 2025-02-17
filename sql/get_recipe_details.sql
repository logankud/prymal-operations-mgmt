SELECT 
    rm.name AS raw_material, 
    rrm.quantity, 
    uom.tag AS unit_of_measure, 
    v.name AS vendor_name
FROM recipe_raw_materials rrm
JOIN raw_materials rm ON rrm.raw_material_id = rm.id
JOIN unit_of_measure uom ON rm.unit_of_measure_id = uom.id
JOIN vendors v ON rm.vendor_id = v.id  -- Join vendors to get vendor name
WHERE rrm.recipe_id = %s;
