SELECT 
    r.id AS recipe_id,
    r.product_id,  -- Ensure product_id is included
    p.name AS product_name,
    r.version,
    r.active,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'name', rm.name,
            'quantity', rr.quantity,
            'unit', u.name
        )
    ) AS raw_materials
FROM recipes r
JOIN products p ON r.product_id = p.id
LEFT JOIN recipe_raw_materials rr ON r.id = rr.recipe_id
LEFT JOIN raw_materials rm ON rr.raw_material_id = rm.id
LEFT JOIN unit_of_measure u ON rm.unit_of_measure_id = u.id
GROUP BY r.id, p.name, r.version, r.active, r.product_id
ORDER BY p.name, r.version DESC;
