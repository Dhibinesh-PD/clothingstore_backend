# Cloth Store &bull; Backend REST API &amp; Server Engine

A secure, high-performance Flask &amp; MySQL 8.0 e-commerce backend powering the **Cloth Store** luxury apparel platform. Features automated frontend template discovery, real-time product catalog search &amp; filtering, multi-method checkout with stock deduction, 3-step OTP password recovery, and an executive administration console.

---

## 🚀 Key Features

- **Dynamic Frontend Discovery**: Seamlessly detects and serves templates and static assets from sibling repositories (`clothingstore_frontend/frontend`) or environment variables.
- **Product Catalog Engine (`GET /api/products`)**:
  - Real-time search by name, gender, or category.
  - Multi-attribute filtering (`gender=Men|Women`, `category=T-Shirt|Shirt|Jeans|Dress`).
  - Dynamic sorting (`price_asc`, `price_desc`, `name_asc`).
  - Luxury metadata computation: star ratings, review counts, discount strikethrough pricing, and badges (*Bestseller*, *Trending*, *Low Stock*, *New Season*).
- **Authentication &amp; Session Management**:
  - Secure customer registration and login with session cookies.
  - Profile retrieval and updating (`GET / PUT /api/profile`).
- **3-Step Password Recovery**:
  - Generates timed 6-digit OTP verification codes.
  - Dedicated APIs: `/api/auth/forgot-password`, `/api/auth/verify-otp`, and `/api/auth/reset-password`.
- **Cart Checkout &amp; Orders**:
  - `POST /buy`: Validates item stocks, creates order records, and deducts inventory.
  - Supports multiple payment methods (`UPI`, `CARD`, `NETBANKING`, `COD`).
  - `POST /orders/cancel/<id>`: Safely cancels pending customer orders and restores inventory.
- **Executive Admin Console**:
  - Real-time revenue, product count, stock levels, and order metrics.
  - MySQL 8.0 connection health monitoring.
  - Full product inventory management (Add, Update, Delete) with HD image previews.
  - Real-time order fulfillment status updates (*Pending*, *Shipped*, *Delivered*, *Cancelled*).

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+ (Tested on Python 3.14)
- **Framework**: Flask 3.1+
- **Database**: MySQL 8.0 / MariaDB
- **Database Driver**: PyMySQL &amp; Cryptography (for `caching_sha2_password` auth)
- **Security**: Werkzeug password hashing, session cookies

---

## 📁 Repository Structure

```
clothingstore_backend/
├── backend/
│   ├── app.py               # Core Flask application, routing, and REST API
│   └── admin.py             # Script to initialize or reset admin account
├── database/
│   ├── schema.sql           # Database tables (users, admins, products, orders)
│   ├── seed_data.sql        # Initial sample products with HD fashion imagery
│   └── update_images.py     # Migration script to update products with HD images
├── requirements.txt         # Pinned Python package dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Installation &amp; Setup

### 1. Prerequisites
- **Python 3.10+** installed and added to `PATH`.
- **MySQL Server 8.0** running locally on port `3306`.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration &amp; Seeding
Ensure MySQL service is running, then configure your credentials in `backend/app.py` under `DB_CONFIG`:

```python
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_mysql_password",
    "database": "clothingstore",
}
```

Initialize the database schema and sample data:
```bash
# Initialize schema & seed data
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed_data.sql

# Update catalog with high-definition fashion photography
python database/update_images.py
```

### 4. Run the Server
```bash
python backend/app.py
```

The server will automatically bind to `http://127.0.0.1:5000`.

---

## 📋 REST API Reference

### Public &amp; Customer Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | Register a new customer account |
| `POST` | `/login` | Authenticate customer and establish session |
| `GET` | `/logout` | Clear user session and sign out |
| `GET` | `/api/products` | Retrieve catalog (supports `?search=`, `?gender=`, `?category=`, `?sort=`) |
| `GET` | `/api/profile` | Retrieve authenticated customer's profile and address |
| `PUT` | `/api/profile` | Update customer address and phone details |
| `POST` | `/buy` | Checkout items, deduct stock, and generate order records |
| `GET` | `/api/my-orders` | Fetch authenticated customer's order history and delivery status |
| `POST` | `/orders/cancel/<id>` | Cancel pending order and restock items |

### Password Recovery Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/forgot-password` | Generate a 6-digit recovery OTP for user's email |
| `POST` | `/api/auth/verify-otp` | Validate the 6-digit OTP code |
| `POST` | `/api/auth/reset-password` | Update account password in database |

### Admin Operations Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/admin/login` | Authenticate administrator session |
| `GET` | `/admin/dashboard` | Executive KPIs, inventory list, and orders queue |
| `POST` | `/admin/products/add` | Add a new product to the catalog |
| `POST` | `/admin/products/update/<id>` | Update an existing product's details and stock |
| `POST` | `/admin/products/delete/<id>` | Delete a product from the database |
| `POST` | `/admin/orders/status/<id>` | Update order status (`Pending`, `Shipped`, `Delivered`, `Cancelled`) |

---

## 🔑 Default Credentials

### Customer Account
- **Email**: `david@example.com`
- **Password**: `password123`
- *(Or click the **Demo Login** button on the sign-in page)*

### Administrator Account
- **Portal URL**: `http://127.0.0.1:5000/admin/login`
- **Email**: `dhi@gmail.com`
- **Password**: `12345`

---

## 🧪 Testing

Run the automated backend test suite:
```bash
python scratch/test_store_app.py
```
Validates routes, authentication, query filtering, OTP workflows, order checkout, and admin dashboard KPI calculations.