import pymysql

from werkzeug.security import generate_password_hash


# ==========================================
# ADMIN DETAILS
# ==========================================

ADMIN_NAME = "Store Admin"

ADMIN_EMAIL = "dhi@gmail.com"

ADMIN_PASSWORD = "12345"



# MYSQL

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "kalaimathiii",
    "database": "clothingstore",
}


connection = pymysql.connect(**DB_CONFIG)

cursor = connection.cursor()


password_hash = generate_password_hash(ADMIN_PASSWORD)


cursor.execute(
    """
    INSERT INTO admins
    (
        name,
        email,
        password
    )

    VALUES
    (
        %s,
        %s,
        %s
    )

    ON DUPLICATE KEY UPDATE

        name = VALUES(name),

        password = VALUES(password)
    """,
    (
        ADMIN_NAME,
        ADMIN_EMAIL,
        password_hash,
    ),
)


connection.commit()


cursor.close()

connection.close()


if __name__ == "__main__":
    print("Admin account created successfully.")
    print("Admin email:", ADMIN_EMAIL)
    print("Admin password:", ADMIN_PASSWORD)
