UPDATE raw_materials
SET total_inventory = total_inventory + %s, updated_at = NOW()
WHERE id = %s;
