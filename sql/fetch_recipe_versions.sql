SELECT id, version, active FROM recipes WHERE product_id = %s ORDER BY version DESC;
