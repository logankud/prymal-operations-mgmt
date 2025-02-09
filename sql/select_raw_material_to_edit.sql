SELECT 
    raw_materials.id,
    raw_materials.name,
    raw_materials.vendor_id,
    vendors.name AS vendor_name,
    raw_materials.unit_of_measure_id,
    unit_of_measure.name AS unit_of_measure_name,
    raw_materials.moq,
    raw_materials.tags,
    raw_materials.created_at,
    raw_materials.updated_at
FROM raw_materials
LEFT JOIN vendors ON raw_materials.vendor_id = vendors.id
LEFT JOIN unit_of_measure ON raw_materials.unit_of_measure_id = unit_of_measure.id
WHERE raw_materials.id = %s;
