SELECT rm.name, rrm.quantity, uom.tag 
FROM recipe_raw_materials rrm
JOIN raw_materials rm ON rrm.raw_material_id = rm.id
JOIN unit_of_measure uom ON rm.unit_of_measure_id = uom.id
WHERE rrm.recipe_id = %s;
