UPDATE raw_materials
SET total_inventory = GREATEST(total_inventory - %s, 0)
WHERE id = %s;
