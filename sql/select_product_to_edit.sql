SELECT id, name, sku, price, description, category_id, flavor_id, size_id
FROM products
WHERE id = %s;
