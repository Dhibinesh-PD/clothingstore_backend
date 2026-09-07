import os
import random
import time
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DYNAMIC FRONTEND RESOLUTION
# Supports running inside clothingstore_backend or from root workspace
candidate_dirs = [
    os.environ.get("FRONTEND_DIR"),
    os.path.abspath(os.path.join(BASE_DIR, "..", "..", "clothingstore_frontend", "frontend")),
    os.path.abspath(os.path.join(BASE_DIR, "..", "clothingstore_frontend", "frontend")),
    os.path.abspath(os.path.join(BASE_DIR, "..", "frontend")),
]
FRONTEND_DIR = None
for c in candidate_dirs:
    if c and os.path.exists(os.path.join(c, "templates")):
        FRONTEND_DIR = c
        break
if not FRONTEND_DIR:
    FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "clothingstore_frontend", "frontend"))

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static"),
)
app.secret_key = "cloth_store_secret_key_pro_luxury_2026"

# In-memory store for OTP reset verification: { email: { "otp": "...", "expires": timestamp } }
OTP_STORE = {}

# DATABASE CONFIGURATION
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "kalaimathiii",
    "database": "clothingstore",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def db_connection_status():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE() AS db, VERSION() AS version, NOW() AS server_time")
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return {
            "connected": True,
            "database": row["db"],
            "version": row["version"],
            "server_time": row["server_time"].strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {
            "connected": False,
            "database": DB_CONFIG["database"],
            "error": str(e),
        }


# =============================================================
# CUSTOMER AUTH & PAGES
# =============================================================

@app.route("/")
def login_page():
    if "user_id" in session:
        return redirect("/home")
    return render_template("login.html")


@app.route("/create.html")
@app.route("/register")
def create_account_page():
    if "user_id" in session:
        return redirect("/home")
    return render_template("create.html")


@app.route("/home")
def home_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template(
        "home.html",
        current_user_id=session.get("user_id"),
        user_name=session.get("user_name", "Customer"),
    )


@app.route("/payment")
def payment_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template(
        "payment.html",
        current_user_id=session.get("user_id"),
        user_name=session.get("user_name", "Customer"),
    )


# PASSWORD RECOVERY ROUTES
@app.route("/forgot-password")
@app.route("/Forgetpass.html")
def forgot_password_page():
    return render_template("Forgetpass.html")


@app.route("/verify-otp")
@app.route("/verification.html")
def verify_otp_page():
    return render_template("verification.html")


@app.route("/reset-password")
@app.route("/confirm.html")
def reset_password_page():
    return render_template("confirm.html")


# =============================================================
# AUTH API ENDPOINTS
# =============================================================

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        phone = data.get("phone", "").strip()
        address = data.get("address", "").strip()
        pincode = data.get("pincode", "").strip()
        password = data.get("password", "").strip()

        if not name or not email or not password:
            return jsonify({"success": False, "message": "All required fields must be filled."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            connection.close()
            return jsonify({"success": False, "message": "An account with this email already exists."})

        cursor.execute(
            """INSERT INTO users (name, email, phone, address, pincode, password)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, email, phone, address, pincode, password),
        )

        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Account created successfully! Please login."})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"success": False, "message": "Registration failed: " + str(e)})


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name, email, phone, address, pincode, password FROM users WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({"success": False, "message": "Invalid email or password."})

        password_stored = user["password"]
        password_matches = False
        try:
            password_matches = check_password_hash(password_stored, password)
        except Exception:
            password_matches = False

        if not password_matches and password_stored == password:
            password_matches = True

        if not password_matches:
            return jsonify({"success": False, "message": "Invalid email or password."})

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_phone"] = user.get("phone", "")
        session["user_address"] = user.get("address", "")
        session["user_pincode"] = user.get("pincode", "")

        return jsonify({"success": True, "message": "Login successful!", "redirect": "/home"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False, "message": "Login failed: " + str(e)})


# OTP PASSWORD RECOVERY APIS
@app.route("/api/auth/forgot-password", methods=["POST"])
def api_forgot_password():
    try:
        data = request.get_json() or {}
        identifier = data.get("email", "").strip().lower()

        if not identifier:
            return jsonify({"success": False, "message": "Please provide an email or phone number."})

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, email, name FROM users WHERE email = %s OR phone = %s",
            (identifier, identifier),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({"success": False, "message": "No customer account found with that email or phone."})

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        OTP_STORE[user["email"]] = {
            "otp": otp,
            "expires": time.time() + 600,  # 10 mins
            "user_id": user["id"],
        }

        return jsonify({
            "success": True,
            "message": "Verification code generated successfully!",
            "email": user["email"],
            "demo_otp": otp,  # provided for instant testing in UI
        })

    except Exception as e:
        print("FORGOT PASS ERROR:", e)
        return jsonify({"success": False, "message": "Error processing request: " + str(e)})


@app.route("/api/auth/verify-otp", methods=["POST"])
def api_verify_otp():
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        otp = data.get("otp", "").strip()

        record = OTP_STORE.get(email)
        if not record:
            return jsonify({"success": False, "message": "No recovery session found. Please start over."})

        if time.time() > record["expires"]:
            return jsonify({"success": False, "message": "Code has expired. Please request a new one."})

        if record["otp"] != otp:
            return jsonify({"success": False, "message": "Invalid code. Please try again."})

        record["verified"] = True
        return jsonify({"success": True, "message": "Code verified! Please set your new password."})

    except Exception as e:
        print("VERIFY OTP ERROR:", e)
        return jsonify({"success": False, "message": "Verification error: " + str(e)})


@app.route("/api/auth/reset-password", methods=["POST"])
def api_reset_password():
    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        new_password = data.get("password", "").strip()

        if not new_password or len(new_password) < 4:
            return jsonify({"success": False, "message": "Password must be at least 4 characters."})

        record = OTP_STORE.get(email)
        if not record or not record.get("verified"):
            return jsonify({"success": False, "message": "Unauthorized reset. Please verify code first."})

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, record["user_id"]))
        cursor.close()
        connection.close()

        OTP_STORE.pop(email, None)
        return jsonify({"success": True, "message": "Password updated successfully! Please login."})

    except Exception as e:
        print("RESET PASS ERROR:", e)
        return jsonify({"success": False, "message": "Reset error: " + str(e)})


# =============================================================
# CUSTOMER PROFILE APIS
# =============================================================

@app.route("/api/profile", methods=["GET", "PUT"])
def get_or_update_profile():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == "PUT":
            data = request.get_json() or {}
            name = data.get("name", "").strip()
            phone = data.get("phone", "").strip()
            address = data.get("address", "").strip()
            pincode = data.get("pincode", "").strip()

            cursor.execute(
                """UPDATE users SET name = %s, phone = %s, address = %s, pincode = %s
                   WHERE id = %s""",
                (name, phone, address, pincode, session["user_id"]),
            )
            session["user_name"] = name
            session["user_phone"] = phone
            session["user_address"] = address
            session["user_pincode"] = pincode

            cursor.close()
            connection.close()
            return jsonify({"success": True, "message": "Profile updated successfully!"})

        cursor.execute(
            "SELECT name, email, phone, address, pincode FROM users WHERE id = %s",
            (session["user_id"],),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if not user:
            return jsonify({"success": False, "message": "User not found."})

        return jsonify({
            "success": True,
            "profile": {
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"] or "",
                "address": user["address"] or "",
                "pincode": user["pincode"] or "",
            },
        })

    except Exception as e:
        print("PROFILE ERROR:", e)
        return jsonify({"success": False, "message": "Unable to process profile."})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =============================================================
# PRODUCT CATALOG API (SEARCH, FILTER, SORT)
# =============================================================

@app.route("/api/products")
def get_products():
    try:
        gender = request.args.get("gender")
        category = request.args.get("category")
        search = request.args.get("search")
        sort = request.args.get("sort")

        query = "SELECT id, name, gender, category, price, image, stock FROM products WHERE 1=1"
        params = []

        if gender and gender.lower() != "all":
            query += " AND gender = %s"
            params.append(gender)

        if category and category.lower() != "all":
            query += " AND category = %s"
            params.append(category)

        if search:
            query += " AND (name LIKE %s OR category LIKE %s OR gender LIKE %s)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        if sort == "price_asc":
            query += " ORDER BY price ASC"
        elif sort == "price_desc":
            query += " ORDER BY price DESC"
        elif sort == "name_asc":
            query += " ORDER BY name ASC"
        else:
            query += " ORDER BY id ASC"

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
        cursor.close()
        connection.close()

        # Augment with rating & original discount price for luxury presentation
        for p in products:
            p["price"] = float(p["price"])
            p["original_price"] = round(p["price"] * 1.4, 2)
            # deterministic rating based on ID for consistency
            p["rating"] = round(4.2 + ((p["id"] * 7) % 8) * 0.1, 1)
            p["reviews_count"] = 24 + ((p["id"] * 13) % 180)
            if p["stock"] <= 15:
                p["badge"] = "Low Stock"
            elif p["id"] in [1, 4, 8, 9, 13]:
                p["badge"] = "Bestseller"
            elif p["id"] in [2, 6, 11, 15]:
                p["badge"] = "Trending"
            else:
                p["badge"] = "New Season"

        return jsonify(products)

    except Exception as e:
        print("PRODUCT ERROR:", e)
        return jsonify([])


# =============================================================
# CHECKOUT & ORDERS
# =============================================================

@app.route("/buy", methods=["POST"])
def buy_product():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        data = request.get_json() or {}
        products_list = data.get("products", [])
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        pincode = data.get("pincode", "").strip()
        address = data.get("address", "").strip()
        payment_method = data.get("payment_method", "CARD").upper()

        if not products_list:
            return jsonify({"success": False, "message": "No products provided."})

        if not name or not phone or not pincode or not address:
            return jsonify({"success": False, "message": "All delivery details are required."})

        connection = get_db_connection()
        cursor = connection.cursor()

        created_order_ids = []

        for item in products_list:
            product_id = item.get("id")
            product_name = item.get("name")
            gender = item.get("gender")
            category = item.get("category")
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity") or item.get("qty") or 1)
            if quantity < 1:
                quantity = 1

            cursor.execute("SELECT id, stock, name, price, gender, category FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product:
                continue

            if product["stock"] <= 0:
                continue

            if product["stock"] < quantity:
                quantity = product["stock"]

            cursor.execute(
                """INSERT INTO orders (product_id, user_id, customer_name, phone, product_name,
                                      gender, category, quantity, price, address, pincode,
                                      payment_status, order_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    product["id"],
                    session["user_id"],
                    name,
                    phone,
                    product_name or product["name"],
                    gender or product["gender"],
                    category or product["category"],
                    quantity,
                    price or product["price"],
                    address,
                    pincode,
                    f"PAID ({payment_method})",
                    "Pending",
                ),
            )
            created_order_ids.append(cursor.lastrowid)

            cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product["id"]))

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Order placed successfully!",
            "order_ids": created_order_ids,
        })

    except Exception as e:
        print("BUY ERROR:", e)
        return jsonify({"success": False, "message": "Order processing failed: " + str(e)})


@app.route("/my-orders")
def my_orders_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template(
        "myorders.html",
        current_user_id=session.get("user_id"),
        user_name=session.get("user_name", "Customer"),
    )


@app.route("/api/my-orders")
def my_orders():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT o.id, o.product_id, o.product_name, o.gender, o.category, o.quantity, o.price,
                      o.address, o.pincode, o.phone, o.customer_name, o.payment_status,
                      o.order_status, o.order_date, p.image
               FROM orders o
               LEFT JOIN products p ON o.product_id = p.id
               WHERE o.user_id = %s
               ORDER BY o.id DESC""",
            (session["user_id"],),
        )
        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        for o in orders:
            o["price"] = float(o["price"])

        return jsonify({"success": True, "orders": orders})

    except Exception as e:
        print("MY ORDERS ERROR:", e)
        return jsonify({"success": False, "message": "Unable to load orders: " + str(e)})


@app.route("/orders/cancel/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, order_status, product_id, quantity FROM orders WHERE id = %s AND user_id = %s",
            (order_id, session["user_id"]),
        )
        order = cursor.fetchone()

        if not order:
            cursor.close()
            connection.close()
            return jsonify({"success": False, "message": "Order not found."})

        if order["order_status"] != "Pending":
            cursor.close()
            connection.close()
            return jsonify({"success": False, "message": f"Cannot cancel order in '{order['order_status']}' status."})

        cursor.execute("UPDATE orders SET order_status = 'Cancelled' WHERE id = %s", (order_id,))

        if order["product_id"]:
            cursor.execute(
                "UPDATE products SET stock = stock + %s WHERE id = %s",
                (order["quantity"], order["product_id"]),
            )

        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Order cancelled successfully. Stock has been restored."})

    except Exception as e:
        print("CANCEL ORDER ERROR:", e)
        return jsonify({"success": False, "message": "Unable to cancel order."})


# =============================================================
# ADMIN AUTH & SUITE
# =============================================================

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return function(*args, **kwargs)
    return wrapper


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if session.get("admin_logged_in"):
            return redirect("/admin/dashboard")
        return render_template("adminlogin.html")

    try:
        data = request.get_json() or {}
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, password FROM admins WHERE email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        connection.close()

        if not admin:
            return jsonify({"success": False, "message": "Invalid admin credentials."})

        password_stored = admin["password"]
        password_matches = False
        try:
            password_matches = check_password_hash(password_stored, password)
        except Exception:
            password_matches = False

        if not password_matches and password_stored == password:
            password_matches = True

        if password_matches:
            session["admin_logged_in"] = True
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["name"]
            return jsonify({"success": True, "message": "Admin login successful!", "redirect": "/admin/dashboard"})

        return jsonify({"success": False, "message": "Invalid admin credentials."})

    except Exception as e:
        print("ADMIN LOGIN ERROR:", e)
        return jsonify({"success": False, "message": "Admin login failed: " + str(e)})


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    return redirect("/admin/login")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        db_status = db_connection_status()

        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total_products = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(stock), 0) AS total FROM products")
        total_stock = cursor.fetchone()["total"]

        cursor.execute("SELECT category, COUNT(*) AS count FROM products GROUP BY category ORDER BY category")
        category_counts = cursor.fetchall()

        cursor.execute("SELECT gender, COUNT(*) AS count FROM products GROUP BY gender ORDER BY gender")
        gender_counts = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM orders")
        total_orders = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(price * quantity), 0) AS total FROM orders WHERE payment_status LIKE 'PAID%'")
        total_sales = float(cursor.fetchone()["total"] or 0)

        cursor.execute("SELECT order_status, COUNT(*) AS count FROM orders GROUP BY order_status ORDER BY order_status")
        status_counts = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_customers = cursor.fetchone()["total"]

        cursor.execute("SELECT id, name, gender, category, price, image, stock FROM products ORDER BY id DESC")
        products = cursor.fetchall()
        for p in products:
            p["price"] = float(p["price"])

        cursor.execute(
            """SELECT o.id, o.customer_name, o.phone, o.product_name, o.gender, o.category,
                      o.quantity, o.price, o.address, o.pincode, o.payment_status,
                      o.order_status, o.order_date,
                      u.name AS user_name, u.email AS customer_email
               FROM orders o
               LEFT JOIN users u ON o.user_id = u.id
               ORDER BY o.id DESC"""
        )
        orders = cursor.fetchall()
        for o in orders:
            o["price"] = float(o["price"])

        cursor.execute("SELECT id, name, email, phone, created_at FROM users ORDER BY id DESC")
        customers = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "admindashboard.html",
            db_status=db_status,
            total_products=total_products,
            total_stock=total_stock,
            total_orders=total_orders,
            total_customers=total_customers,
            total_sales=round(total_sales, 2),
            category_counts=category_counts,
            gender_counts=gender_counts,
            status_counts=status_counts,
            products=products,
            orders=orders,
            customers=customers,
            admin_name=session.get("admin_name", "Admin"),
        )

    except Exception as e:
        print("DASHBOARD ERROR:", e)
        return render_template(
            "admindashboard.html",
            db_status=db_connection_status(),
            total_products=0,
            total_stock=0,
            total_orders=0,
            total_customers=0,
            total_sales=0,
            category_counts=[],
            gender_counts=[],
            status_counts=[],
            products=[],
            orders=[],
            customers=[],
            admin_name="Admin",
        )


@app.route("/admin/products/add", methods=["POST"])
@admin_required
def add_product():
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        gender = data.get("gender", "").strip()
        category = data.get("category", "").strip()
        price = data.get("price")
        image = data.get("image", "").strip()
        stock = data.get("stock")

        if not name or not gender or not category or price is None or stock is None:
            return jsonify({"success": False, "message": "All product fields are required."})

        if not image:
            image = "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80"

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO products (name, gender, category, price, image, stock)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, gender, category, float(price), image, int(stock)),
        )
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product added successfully!"})

    except Exception as e:
        print("ADD PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to add product: " + str(e)})


@app.route("/admin/products/update/<int:product_id>", methods=["POST"])
@admin_required
def update_product(product_id):
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        gender = data.get("gender", "").strip()
        category = data.get("category", "").strip()
        price = data.get("price")
        image = data.get("image", "").strip()
        stock = data.get("stock")

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE products
               SET name = %s, gender = %s, category = %s, price = %s, image = %s, stock = %s
               WHERE id = %s""",
            (name, gender, category, float(price), image, int(stock), product_id),
        )
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product updated successfully!"})

    except Exception as e:
        print("UPDATE PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to update product: " + str(e)})


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product deleted successfully!"})

    except Exception as e:
        print("DELETE PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to delete product: " + str(e)})


@app.route("/admin/orders/status/<int:order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id):
    try:
        data = request.get_json() or {}
        status = data.get("status")

        valid_statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
        if status not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid order status."})

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE orders SET order_status = %s WHERE id = %s", (status, order_id))
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": f"Order #{order_id} marked as {status}!"})

    except Exception as e:
        print("UPDATE ORDER STATUS ERROR:", e)
        return jsonify({"success": False, "message": "Unable to update order status: " + str(e)})


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":
    print("Frontend dir resolved to:", FRONTEND_DIR)
    app.run(host="0.0.0.0", port=5000, debug=True)
