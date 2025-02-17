SELECT id, name
FROM products
WHERE name ILIKE %s
ORDER BY name ASC;
