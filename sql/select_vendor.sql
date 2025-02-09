SELECT 
    id, 
    name, 
    email, 
    address, 
    description, 
    notes 
FROM 
    vendors 
WHERE 
    id = %s;
