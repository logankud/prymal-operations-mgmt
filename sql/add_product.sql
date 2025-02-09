INSERT INTO products (name, sku, price, description, category_id, flavor_id, size_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id;

