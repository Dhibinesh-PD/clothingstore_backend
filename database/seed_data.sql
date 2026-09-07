-- CLOTH STORE - SAMPLE DATA SEED
-- Run after schema.sql

USE clothingstore;

-- SAMPLE PRODUCTS WITH HD FASHION PHOTOGRAPHY

INSERT INTO products (id, name, gender, category, price, image, stock) VALUES
    (1,  'Classic White T-Shirt',  'Men',   'T-Shirt', 499.00,  'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80', 50),
    (2,  'Black Formal Shirt',     'Men',   'Shirt',   999.00,  'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80', 30),
    (3,  'Slim Fit Blue Jeans',    'Men',   'Jeans',   1499.00, 'https://images.unsplash.com/photo-1542272604-780c96856592?auto=format&fit=crop&w=800&q=80', 40),
    (4,  'Floral Summer Dress',    'Women', 'Dress',   1999.00, 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80', 25),
    (5,  'Casual Striped T-Shirt', 'Women', 'T-Shirt', 599.00,  'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=800&q=80', 45),
    (6,  'Sky Blue Formal Shirt',  'Men',   'Shirt',   1099.00, 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80', 20),
    (7,  'Skinny Black Jeans',     'Women', 'Jeans',   1599.00, 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80', 35),
    (8,  'Red Evening Dress',      'Women', 'Dress',   2499.00, 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=800&q=80', 15),
    (9,  'Elegant Black Gown',     'Women', 'Dress',   2999.00, 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80', 18),
    (10, 'Pastel Pink Midi Dress', 'Women', 'Dress',   1799.00, 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?auto=format&fit=crop&w=800&q=80', 22),
    (11, 'Sparkling Sequin Dress', 'Women', 'Dress',   3499.00, 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80', 12),
    (12, 'Boho Maxi Dress',        'Women', 'Dress',   2199.00, 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=800&q=80', 16),
    (13, 'Party Cocktail Dress',   'Women', 'Dress',   2799.00, 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80', 20),
    (14, 'Casual Denim Dress',     'Women', 'Dress',   1599.00, 'https://images.unsplash.com/photo-1582533561751-ef6f6ab93a2e?auto=format&fit=crop&w=800&q=80', 28),
    (15, 'Silk Evening Gown',      'Women', 'Dress',   3999.00, 'https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=800&q=80', 10),
    (16, 'Summer Beach Dress',     'Women', 'Dress',   1299.00, 'https://images.unsplash.com/photo-1508427953056-b00b8d78ebf5?auto=format&fit=crop&w=800&q=80', 35)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    gender = VALUES(gender),
    category = VALUES(category),
    price = VALUES(price),
    image = VALUES(image),
    stock = VALUES(stock);
