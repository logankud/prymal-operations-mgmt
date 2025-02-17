INSERT INTO product_snapshots (
  product_id, snapshot_version, name, sku, category_id, category_name, flavor_id, flavor_name, size_id, size_name
)
SELECT 
  p.id, 
  COALESCE((SELECT MAX(snapshot_version) + 1 FROM product_snapshots WHERE product_id = p.id), 1),
  p.name, p.sku, 
  c.id AS category_id, c.name AS category_name, 
  f.id AS flavor_id, f.name AS flavor_name, 
  s.id AS size_id, s.name AS size_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN flavors f ON p.flavor_id = f.id
LEFT JOIN sizes s ON p.size_id = s.id
WHERE p.id = %s;
