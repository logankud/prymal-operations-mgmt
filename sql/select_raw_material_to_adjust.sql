SELECT id, name, vendor_id, unit_of_measure_id, moq, total_inventory, reserved_inventory, available_inventory
FROM raw_materials
WHERE id = %s;
