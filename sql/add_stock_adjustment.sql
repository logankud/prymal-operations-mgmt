INSERT INTO stock_adjustments (raw_material_id, adjustment_amount, unit_of_measure, reason, created_at)
VALUES (%s, %s, %s, %s, NOW());
