INSERT INTO product_snapshots (
  product_id,
  snapshot_version,
  name,
  sku,
  category_id,
  category_name,
  flavor_id,
  flavor_name,
  size_id,
  size_name,
  recipe_version,
  created_at
)
VALUES (
  %s,
  COALESCE((SELECT MAX(snapshot_version) + 1 FROM product_snapshots WHERE product_id = %s), 1),
  %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
)
RETURNING id;
