INSERT INTO flavors (name)
VALUES (%s)
RETURNING id;
