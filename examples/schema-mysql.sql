-- Apply only to a separately created empty teaching database.
-- Verify SELECT VERSION(): XAMPP commonly supplies MariaDB.
CREATE TABLE products (
    id integer PRIMARY KEY,
    name varchar(200) NOT NULL,
    price decimal(12,2) NOT NULL CHECK (price >= 0),
    version integer NOT NULL DEFAULT 1
) ENGINE=InnoDB;
INSERT INTO products(id, name, price) VALUES (7, 'Блокнот', 125.50), (8, 'Ручка', 80.00);
