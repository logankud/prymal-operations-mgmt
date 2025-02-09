SELECT rm.id, rm.available_quantity, rm.accounted_quantity, bom.quantity_per_unit
FROM bill_of_materials bom
JOIN raw_materials rm ON bom.raw_material_id = rm.id
WHERE bom.product_id = %s;
