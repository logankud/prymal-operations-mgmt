INSERT INTO recipes (product_id, version)
VALUES (%s, (SELECT COALESCE(MAX(version), 0) + 1 FROM recipes WHERE product_id = %s))
RETURNING id, version;
