INSERT INTO sizes (name, weight_g)
VALUES (%s, %s)
RETURNING id;
