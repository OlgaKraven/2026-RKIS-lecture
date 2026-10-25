-- Apply only to a separately created empty teaching database.
CREATE TABLE products (
    id integer PRIMARY KEY,
    name text NOT NULL,
    price numeric(12,2) NOT NULL CHECK (price >= 0),
    version integer NOT NULL DEFAULT 1
);
INSERT INTO products(id, name, price) VALUES (7, 'Блокнот', 125.50), (8, 'Ручка', 80.00);
