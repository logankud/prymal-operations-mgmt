UPDATE recipes SET active = FALSE WHERE product_id = (SELECT product_id FROM recipes WHERE id = %s);
