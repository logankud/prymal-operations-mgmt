SELECT 
    rm.id, 
    rm.name, 
    v.name AS vendor_name, 
    uom.name AS unit_of_measure, 
    uom.tag AS unit_abbreviation,  -- e.g., "kg", "g", "lb"
    rm.moq, 
    rm.total_inventory, 
    rm.reserved_inventory, 
    rm.available_inventory, 
    rm.created_at, 
    rm.updated_at
FROM raw_materials rm
LEFT JOIN vendors v ON rm.vendor_id = v.id
LEFT JOIN unit_of_measure uom ON rm.unit_of_measure_id = uom.id
WHERE rm.id = %s;
