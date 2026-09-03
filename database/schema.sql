
-- CLOTH STORE - DATABASE SCHEMA
-- Database: clothingstore

CREATE DATABASE IF NOT EXISTS clothingstore
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE clothingstore;

-- USERS (Customers)

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL DEFAULT '',
    address TEXT,
    pincode VARCHAR(10) NOT NULL DEFAULT '',
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADMINS

CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCTS

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    gender ENUM('Men', 'Women') NOT NULL,
    category ENUM('T-Shirt', 'Shirt', 'Jeans', 'Dress') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    image TEXT,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ORDERS

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NULL,
    user_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL DEFAULT '',
    phone VARCHAR(20) NOT NULL DEFAULT '',
    product_name VARCHAR(150) NOT NULL,
    gender ENUM('Men', 'Women'),
    category ENUM('T-Shirt', 'Shirt', 'Jeans', 'Dress'),
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10, 2),
    address TEXT NOT NULL,
    pincode VARCHAR(10) NOT NULL DEFAULT '',
    payment_status VARCHAR(20) DEFAULT 'PAID',
    order_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

