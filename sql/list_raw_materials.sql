SELECT 
    rm.id, 
    rm.name, 
    v.name AS vendor_name, 
    uom.name AS unit_of_measure, 
    rm.moq, 
    rm.total_inventory,
    rm.reserved_inventory,
    rm.available_inventory,
    rm.tags, 
    rm.created_at, 
    rm.updated_at
FROM 
    raw_materials rm
JOIN 
    vendors v ON rm.vendor_id = v.id
JOIN 
    unit_of_measure uom ON rm.unit_of_measure_id = uom.id
ORDER BY 
    rm.name;
