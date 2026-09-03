import os

from flask import Flask, render_template, request, jsonify, session, redirect
import pymysql
from functools import wraps
from werkzeug.security import check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static"),
)
app.secret_key = "cloth_store_secret_key"


# DATABASE CONFIGURATION

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "kalaimathiii",
    "database": "clothingstore",
    "cursorclass": pymysql.cursors.DictCursor,
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


# CUSTOMER ROUTES

@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/create.html")
def create_account_page():
    return render_template("create.html")


@app.route("/home")
def home_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("home.html", current_user_id=session.get("user_id"))


@app.route("/payment")
def payment_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("payment.html", current_user_id=session.get("user_id"))


# CUSTOMER REGISTER

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone", "")
        address = data.get("address", "")
        pincode = data.get("pincode", "")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"success": False, "message": "All fields are required."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            connection.close()
            return jsonify({"success": False, "message": "Email already exists."})

        cursor.execute(
            "INSERT INTO users (name, email, phone, address, pincode, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, phone, address, pincode, password),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Account created successfully!"})

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"success": False, "message": "Registration failed."})



# CUSTOMER LOGIN

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

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

        if user["password"] != password:
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
        return jsonify({"success": False, "message": "Login failed."})


# =============================================
# CUSTOMER PROFILE API
# =============================================

@app.route("/api/profile")
def get_profile():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        connection = get_db_connection()
        cursor = connection.cursor()

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
                "phone": user["phone"],
                "address": user["address"],
                "pincode": user["pincode"],
            },
        })

    except Exception as e:
        print("PROFILE ERROR:", e)
        return jsonify({"success": False, "message": "Unable to load profile."})



# CUSTOMER LOGOUT

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# PRODUCT API

@app.route("/api/products")
def get_products():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name, gender, category, price, image, stock FROM products ORDER BY id"
        )

        products = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(products)

    except Exception as e:
        print("PRODUCT ERROR:", e)
        return jsonify([])



# BUY PRODUCTS (CART CHECKOUT)

@app.route("/buy", methods=["POST"])
def buy_product():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        data = request.get_json()
        products_list = data.get("products", [])
        name = data.get("name")
        phone = data.get("phone")
        pincode = data.get("pincode")
        address = data.get("address")

        if not products_list:
            return jsonify({"success": False, "message": "No products provided."})

        if not name or not phone or not pincode or not address:
            return jsonify({"success": False, "message": "All fields are required."})

        connection = get_db_connection()
        cursor = connection.cursor()

        for item in products_list:
            product_name = item.get("name")
            gender = item.get("gender")
            category = item.get("category")
            price = item.get("price")
            product_id = item.get("id")
            quantity = int(item.get("quantity") or item.get("qty") or 1)

            if quantity < 1:
                quantity = 1

            cursor.execute("SELECT id, stock FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product:
                continue

            if product["stock"] <= 0:
                continue

            if product["stock"] < quantity:
                quantity = product["stock"]

            cursor.execute(
                """INSERT INTO orders (product_id, user_id, customer_name, phone, product_name, gender, category, quantity, price, address, pincode, payment_status, order_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (product["id"], session["user_id"], name, phone, product_name, gender, category, quantity, price, address, pincode, "PAID", "Pending"),
            )

            cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product["id"]))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Order placed successfully!"})

    except Exception as e:
        print("BUY ERROR:", e)
        return jsonify({"success": False, "message": "Order failed."})


# =============================================
# CUSTOMER MY ORDERS PAGE
# =============================================

@app.route("/my-orders")
def my_orders_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("myorders.html")


# =============================================
# CUSTOMER ORDERS API
# =============================================

@app.route("/api/my-orders")
def my_orders():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Please login first."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT id, product_name, gender, category, quantity, price,
                      address, pincode, phone, customer_name, payment_status,
                      order_status, order_date
               FROM orders
               WHERE user_id = %s
               ORDER BY id DESC""",
            (session["user_id"],),
        )
        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "orders": orders})

    except Exception as e:
        print("MY ORDERS ERROR:", e)
        return jsonify({"success": False, "message": "Unable to load orders."})


# =============================================
# CUSTOMER CANCEL ORDER
# =============================================

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
            return jsonify({"success": False, "message": "Only pending orders can be cancelled."})

        cursor.execute(
            "UPDATE orders SET order_status = 'Cancelled' WHERE id = %s",
            (order_id,),
        )

        cursor.execute(
            "UPDATE products SET stock = stock + %s WHERE id = %s",
            (order["quantity"], order["product_id"]),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Order cancelled successfully!"})

    except Exception as e:
        print("CANCEL ORDER ERROR:", e)
        return jsonify({"success": False, "message": "Unable to cancel order."})


# ADMIN ROUTES

@app.route("/admin/login")
def admin_login_page():
    return render_template("adminlogin.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name, email, password FROM admins WHERE email = %s",
            (email,),
        )

        admin = cursor.fetchone()
        cursor.close()
        connection.close()

        if not admin:
            return jsonify({"success": False, "message": "Invalid admin email or password."})

        password_stored = admin["password"]
        password_matches = False
        try:
            password_matches = check_password_hash(password_stored, password)
        except Exception:
            password_matches = password_stored == password

        if password_matches:
            session["admin_logged_in"] = True
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["name"]
            return jsonify({"success": True, "message": "Admin login successful!", "redirect": "/admin/dashboard"})

        return jsonify({"success": False, "message": "Invalid admin email or password."})

    except Exception as e:
        print("ADMIN LOGIN ERROR:", e)
        return jsonify({"success": False, "message": "Admin login failed."})


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return function(*args, **kwargs)

    return wrapper


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    return redirect("/admin/login")



# ADMIN DASHBOARD

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        db_status = db_connection_status()

        # ===== PRODUCTS SUMMARY =====
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total_products = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(stock), 0) AS total FROM products")
        total_stock = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT category, COUNT(*) AS count FROM products GROUP BY category ORDER BY category"
        )
        category_counts = cursor.fetchall()

        cursor.execute(
            "SELECT gender, COUNT(*) AS count FROM products GROUP BY gender ORDER BY gender"
        )
        gender_counts = cursor.fetchall()

        # ===== ORDERS SUMMARY =====
        cursor.execute("SELECT COUNT(*) AS total FROM orders")
        total_orders = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COALESCE(SUM(price * quantity), 0) AS total FROM orders WHERE payment_status = 'PAID'"
        )
        total_sales = cursor.fetchone()["total"]

        cursor.execute(
            """SELECT order_status, COUNT(*) AS count FROM orders
               GROUP BY order_status ORDER BY order_status"""
        )
        status_counts = cursor.fetchall()

        # ===== CUSTOMERS SUMMARY =====
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_customers = cursor.fetchone()["total"]

        # ===== FULL LISTS =====
        cursor.execute(
            "SELECT id, name, gender, category, price, image, stock FROM products ORDER BY id DESC"
        )
        products = cursor.fetchall()

        cursor.execute(
            """SELECT orders.id, orders.customer_name, orders.phone, orders.product_name, orders.gender, orders.category,
                      orders.quantity, orders.price, orders.address, orders.pincode, orders.payment_status,
                      orders.order_status, orders.order_date,
                      users.name AS user_name, users.email AS customer_email
               FROM orders
               JOIN users ON orders.user_id = users.id
               ORDER BY orders.id DESC"""
        )
        orders = cursor.fetchall()

        cursor.execute("SELECT id, name, email FROM users ORDER BY id DESC")
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
            total_sales=total_sales,
            category_counts=category_counts,
            gender_counts=gender_counts,
            status_counts=status_counts,
            products=products,
            orders=orders,
            customers=customers,
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
        )


# ADMIN PRODUCT MANAGEMENT


@app.route("/admin/products/add", methods=["POST"])
@admin_required
def add_product():
    try:
        data = request.get_json()
        name = data.get("name")
        gender = data.get("gender")
        category = data.get("category")
        price = data.get("price")
        image = data.get("image")
        stock = data.get("stock")

        if not name or not gender or not category or price is None or stock is None:
            return jsonify({"success": False, "message": "All product fields are required."})

        stock = int(stock)
        price = float(price)

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """INSERT INTO products (name, gender, category, price, image, stock)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, gender, category, price, image, stock),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product added successfully!"})

    except Exception as e:
        print("ADD PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to add product."})


@app.route("/admin/products/update/<int:product_id>", methods=["POST"])
@admin_required
def update_product(product_id):
    try:
        data = request.get_json()
        name = data.get("name")
        gender = data.get("gender")
        category = data.get("category")
        price = data.get("price")
        image = data.get("image")
        stock = data.get("stock")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """UPDATE products
               SET name = %s, gender = %s, category = %s, price = %s, image = %s, stock = %s
               WHERE id = %s""",
            (name, gender, category, price, image, stock, product_id),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product updated successfully!"})

    except Exception as e:
        print("UPDATE PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to update product."})


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Product deleted successfully!"})

    except Exception as e:
        print("DELETE PRODUCT ERROR:", e)
        return jsonify({"success": False, "message": "Unable to delete product."})


# ADMIN ORDER STATUS MANAGEMENT

@app.route("/admin/orders/status/<int:order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        status = data.get("status")

        valid_statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
        if status not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid order status."})

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE orders SET order_status = %s WHERE id = %s",
            (status, order_id),
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Order status updated!"})

    except Exception as e:
        print("UPDATE ORDER STATUS ERROR:", e)
        return jsonify({"success": False, "message": "Unable to update order status."})


# RUN APPLICATION

if __name__ == "__main__":
    app.run(debug=True)
