SELECT 
    ri.id, rm.name AS raw_material_name, ri.quantity
FROM 
    recipe_items ri
JOIN 
    raw_materials rm ON ri.raw_material_id = rm.id
WHERE 
    ri.recipe_id = %s;
