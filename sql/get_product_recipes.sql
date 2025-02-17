SELECT 
    id AS recipe_id, 
    version AS recipe_version, 
    created_at
FROM recipes
WHERE product_id = %s
ORDER BY version DESC;
