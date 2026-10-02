-- Dragon Wok: schema + sample data for MySQL 8 / Amazon RDS MySQL.
-- Generated from alembic/versions/0001_initial.py. Use EITHER this file OR `alembic upgrade head`, not both.
-- The admin user is created with:  python -m app.db.seed  (needs SEED_ADMIN_PASSWORD).
SET NAMES utf8mb4;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001

CREATE TABLE users (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    phone VARCHAR(20) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    `role` VARCHAR(20) NOT NULL DEFAULT 'customer', 
    created_at DATETIME NOT NULL DEFAULT now(), 
    PRIMARY KEY (id), 
    CONSTRAINT ck_users_role CHECK (role IN ('customer','admin'))
)ENGINE=InnoDB CHARSET=utf8mb4;

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE categories (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    created_at DATETIME NOT NULL DEFAULT now(), 
    PRIMARY KEY (id), 
    UNIQUE (name)
)ENGINE=InnoDB CHARSET=utf8mb4;

CREATE TABLE menu_items (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    category_id INTEGER NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    description TEXT, 
    price NUMERIC(10, 2) NOT NULL, 
    image_url VARCHAR(500), 
    food_type VARCHAR(10) NOT NULL DEFAULT 'veg', 
    is_available BOOL NOT NULL DEFAULT true, 
    created_at DATETIME NOT NULL DEFAULT now(), 
    updated_at DATETIME NOT NULL DEFAULT now(), 
    PRIMARY KEY (id), 
    CONSTRAINT ck_menu_items_price_positive CHECK (price > 0), 
    CONSTRAINT ck_menu_items_food_type CHECK (food_type IN ('veg','non_veg')), 
    FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE RESTRICT
)ENGINE=InnoDB CHARSET=utf8mb4;

CREATE INDEX ix_menu_items_name ON menu_items (name);

CREATE INDEX ix_menu_items_category_available ON menu_items (category_id, is_available);

CREATE TABLE orders (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    user_id INTEGER NOT NULL, 
    order_number VARCHAR(32) NOT NULL, 
    total_amount NUMERIC(10, 2) NOT NULL, 
    delivery_fee NUMERIC(10, 2) NOT NULL DEFAULT '0.00', 
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT '0.00', 
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cod', 
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending', 
    order_status VARCHAR(20) NOT NULL DEFAULT 'pending', 
    customer_name VARCHAR(100) NOT NULL, 
    customer_phone VARCHAR(20) NOT NULL, 
    delivery_address TEXT NOT NULL, 
    special_instructions TEXT, 
    created_at DATETIME NOT NULL DEFAULT now(), 
    updated_at DATETIME NOT NULL DEFAULT now(), 
    PRIMARY KEY (id), 
    CONSTRAINT ck_orders_status CHECK (order_status IN ('pending','confirmed','preparing','out_for_delivery','delivered','cancelled')), 
    CONSTRAINT ck_orders_payment_status CHECK (payment_status IN ('pending','paid','failed','refunded')), 
    CONSTRAINT ck_orders_total_nonneg CHECK (total_amount >= 0), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT, 
    UNIQUE (order_number)
)ENGINE=InnoDB CHARSET=utf8mb4;

CREATE INDEX ix_orders_user_created ON orders (user_id, created_at);

CREATE INDEX ix_orders_status ON orders (order_status);

CREATE TABLE order_items (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    order_id INTEGER NOT NULL, 
    menu_item_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    unit_price NUMERIC(10, 2) NOT NULL, 
    subtotal NUMERIC(10, 2) NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_order_items_qty_positive CHECK (quantity > 0), 
    FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
    FOREIGN KEY(menu_item_id) REFERENCES menu_items (id) ON DELETE RESTRICT
)ENGINE=InnoDB CHARSET=utf8mb4;

CREATE INDEX ix_order_items_order_id ON order_items (order_id);

CREATE INDEX ix_order_items_menu_item_id ON order_items (menu_item_id);

INSERT INTO alembic_version (version_num) VALUES ('0001');

-- Sample data
INSERT INTO categories (name, description) VALUES ('Chinese Starters', 'Crispy, saucy bites to begin your meal');
INSERT INTO categories (name, description) VALUES ('Noodles', 'Wok-tossed noodles with smoky wok hei');
INSERT INTO categories (name, description) VALUES ('Fried Rice', 'Fragrant rice fried on high heat');
INSERT INTO categories (name, description) VALUES ('Chinese Main Course', 'Rich gravies and dry specials');
INSERT INTO categories (name, description) VALUES ('Soups', 'Hot bowls, made fresh every day');
INSERT INTO categories (name, description) VALUES ('Momos', 'Hand-folded dumplings, steamed or fried');
INSERT INTO categories (name, description) VALUES ('Desserts', 'A sweet end to dinner');
INSERT INTO categories (name, description) VALUES ('Beverages', 'Cool drinks and coffee');
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Spring Rolls', 'Crisp rolls filled with cabbage, carrot and glass noodles.', 149.00, '/images/starters.svg', 'veg', 1 FROM categories WHERE name = 'Chinese Starters';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chilli Paneer', 'Paneer cubes tossed with capsicum, onion and a spicy soy glaze.', 229.00, '/images/starters.svg', 'veg', 1 FROM categories WHERE name = 'Chinese Starters';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chilli Chicken', 'Crispy chicken in a hot garlic and green chilli sauce.', 269.00, '/images/starters.svg', 'non_veg', 1 FROM categories WHERE name = 'Chinese Starters';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Veg Manchurian', 'Golden vegetable balls in a tangy ginger-garlic sauce.', 199.00, '/images/starters.svg', 'veg', 1 FROM categories WHERE name = 'Chinese Starters';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken Manchurian', 'Fried chicken in a bold, tangy Manchurian sauce.', 259.00, '/images/starters.svg', 'non_veg', 1 FROM categories WHERE name = 'Chinese Starters';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Veg Hakka Noodles', 'Thin noodles tossed with crunchy vegetables and soy.', 169.00, '/images/noodles.svg', 'veg', 1 FROM categories WHERE name = 'Noodles';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken Hakka Noodles', 'Wok noodles with shredded chicken, egg and spring onion.', 209.00, '/images/noodles.svg', 'non_veg', 1 FROM categories WHERE name = 'Noodles';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Veg Fried Rice', 'Long-grain rice stir-fried with vegetables and spring onion.', 159.00, '/images/rice.svg', 'veg', 1 FROM categories WHERE name = 'Fried Rice';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken Fried Rice', 'Rice fried with chicken, egg and a hint of pepper.', 199.00, '/images/rice.svg', 'non_veg', 1 FROM categories WHERE name = 'Fried Rice';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Veg Manchurian Gravy', 'Vegetable balls simmered in a thick Manchurian gravy.', 219.00, '/images/main.svg', 'veg', 1 FROM categories WHERE name = 'Chinese Main Course';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken in Hot Garlic Sauce', 'Tender chicken in a deep garlic and chilli gravy.', 289.00, '/images/main.svg', 'non_veg', 1 FROM categories WHERE name = 'Chinese Main Course';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Hot and Sour Soup', 'Peppery, tangy soup with vegetables and tofu.', 129.00, '/images/soups.svg', 'veg', 1 FROM categories WHERE name = 'Soups';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken Sweet Corn Soup', 'Silky soup with sweet corn and shredded chicken.', 149.00, '/images/soups.svg', 'non_veg', 1 FROM categories WHERE name = 'Soups';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Veg Momos', 'Steamed dumplings with cabbage, carrot and herbs (8 pcs).', 119.00, '/images/momos.svg', 'veg', 1 FROM categories WHERE name = 'Momos';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chicken Momos', 'Steamed dumplings with juicy minced chicken (8 pcs).', 149.00, '/images/momos.svg', 'non_veg', 1 FROM categories WHERE name = 'Momos';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Chocolate Brownie', 'Warm fudgy brownie with a dusting of cocoa.', 129.00, '/images/desserts.svg', 'veg', 1 FROM categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Honey Noodles with Ice Cream', 'Crisp fried noodles in honey with vanilla ice cream.', 169.00, '/images/desserts.svg', 'veg', 1 FROM categories WHERE name = 'Desserts';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Cold Coffee', 'Chilled coffee blended with milk and ice.', 119.00, '/images/beverages.svg', 'veg', 1 FROM categories WHERE name = 'Beverages';
INSERT INTO menu_items (category_id, name, description, price, image_url, food_type, is_available) SELECT id, 'Lemon Iced Tea', 'Fresh lemon and black tea over ice.', 99.00, '/images/beverages.svg', 'veg', 1 FROM categories WHERE name = 'Beverages';
