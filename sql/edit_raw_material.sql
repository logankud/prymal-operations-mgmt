UPDATE raw_materials
SET 
    name = %s, 
    vendor_id = %s, 
    unit_of_measure_id = %s, 
    moq = %s, 
    tags = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE 
    id = %s;
