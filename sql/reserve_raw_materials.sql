UPDATE raw_materials 
SET available_quantity = available_quantity - %s, 
    accounted_quantity = accounted_quantity + %s 
WHERE id = %s;
