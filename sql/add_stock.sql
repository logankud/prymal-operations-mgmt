UPDATE raw_materials
SET total_inventory = total_inventory + %s
WHERE id = %s;
