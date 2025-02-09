SELECT 
    r.id AS recipe_id,
    p.name AS product_name,
    json_agg(json_build_object('name', rm.name, 'quantity', rrm.quantity, 'unit', uom.tag)) AS raw_materials
FROM recipes r
JOIN products p ON r.product_id = p.id
JOIN recipe_raw_materials rrm ON r.id = rrm.recipe_id
JOIN raw_materials rm ON rrm.raw_material_id = rm.id
JOIN unit_of_measure uom ON rm.unit_of_measure_id = uom.id
GROUP BY r.id, p.name;
