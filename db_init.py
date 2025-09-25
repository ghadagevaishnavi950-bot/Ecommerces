import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "ecommerce.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -----------------------------
    # Create Users table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Email TEXT,
            Role TEXT CHECK(Role IN ('Customer','Seller','Admin')) NOT NULL DEFAULT 'Customer'
        )
    """)

    # -----------------------------
    # Create Products table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Price REAL NOT NULL,
            Stock INTEGER NOT NULL,
            SellerID INTEGER,
            FOREIGN KEY (SellerID) REFERENCES Users(UserID)
        )
    """)

    # -----------------------------
    # Create Orders table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
    """)

    # -----------------------------
    # Add default users (Admin, Seller, Customer)
    # -----------------------------
    default_users = [
        ("admin", "admin123", "admin@example.com", "Admin"),
        ("seller1", "seller123", "seller1@example.com", "Seller"),
        ("customer1", "cust123", "customer1@example.com", "Customer"),
    ]

    for username, password, email, role in default_users:
        hashed = generate_password_hash(password)
        try:
            cur.execute(
                "INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)",
                (username, hashed, email, role),
            )
            print(f"Default user created: {username} / {password} ({role})")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists.")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
