SELECT 
    p.id, 
    p.name, 
    s.weight_g 
FROM 
    products p
JOIN 
    sizes s ON p.size_id = s.id;
