UPDATE vendors
SET 
    name = %s, 
    email = %s, 
    address = %s, 
    description = %s, 
    notes = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s;
