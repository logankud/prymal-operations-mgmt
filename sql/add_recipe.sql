INSERT INTO recipes (product_id) 
VALUES (%s) 
RETURNING id;
