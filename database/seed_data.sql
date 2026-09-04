-- CLOTH STORE - SAMPLE DATA SEED
-- Run after schema.sql

USE clothingstore;

-- ADMIN (password must be hashed - use backend/admin.py
-- which inserts a werkzeug-hashed admin account)

-- SAMPLE PRODUCTS

INSERT INTO products (name, gender, category, price, image, stock) VALUES
    ('Classic White T-Shirt',  'Men',   'T-Shirt', 499.00,  '<span>👕</span>', 50),
    ('Black Formal Shirt',     'Men',   'Shirt',   999.00,  '<span>👔</span>', 30),
    ('Slim Fit Blue Jeans',    'Men',   'Jeans',   1499.00, '<span>👖</span>', 40),
    ('Floral Summer Dress',    'Women', 'Dress',   1999.00, '<span>👗</span>', 25),
    ('Casual Striped T-Shirt', 'Women', 'T-Shirt', 599.00,  '<span>👚</span>', 45),
    ('Sky Blue Formal Shirt',  'Men',   'Shirt',   1099.00, '<span>👔</span>', 20),
    ('Skinny Black Jeans',     'Women', 'Jeans',   1599.00, '<span>👖</span>', 35),
    ('Red Evening Dress',      'Women', 'Dress',   2499.00, '<span>👗</span>', 15),
    ('Elegant Black Gown',     'Women', 'Dress',   2999.00, '<span>👜</span>', 18),
    ('Pastel Pink Midi Dress', 'Women', 'Dress',   1799.00, '<span>👚</span>', 22),
    ('Sparkling Sequin Dress', 'Women', 'Dress',   3499.00, '<span>✨👗</span>', 12),
    ('Boho Maxi Dress',        'Women', 'Dress',   2199.00, '<span>👘</span>', 16),
    ('Party Cocktail Dress',   'Women', 'Dress',   2799.00, '<span>🎉</span>', 20),
    ('Casual Denim Dress',     'Women', 'Dress',   1599.00, '<span>👖</span>', 28),
    ('Silk Evening Gown',      'Women', 'Dress',   3999.00, '<span>💎</span>', 10),
    ('Summer Beach Dress',     'Women', 'Dress',   1299.00, '<span>🏖️</span>', 35);
