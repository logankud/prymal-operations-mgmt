UPDATE raw_materials 
SET accounted_quantity = accounted_quantity - %s 
WHERE id = %s;
