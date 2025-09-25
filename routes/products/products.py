from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3

products_bp = Blueprint("products", __name__, url_prefix="/products")
DB_PATH = "ecommerce.db"

# ---------------------------
# Database connection
# ---------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# List products (role-based)
# ---------------------------
@products_bp.route("/list")
def list_products():
    conn = get_db()
    cur = conn.cursor()

    if current_user.is_authenticated:
        if current_user.role == "Seller":
           
            cur.execute("""
                SELECT p.*, u.Username as SellerName
                FROM Products p
                LEFT JOIN Users u ON p.SellerID = u.UserID
                WHERE p.SellerID = ?
            """, (current_user.id,))
        elif current_user.role == "Admin":
            
            cur.execute("""
                SELECT p.*, u.Username as SellerName
                FROM Products p
                LEFT JOIN Users u ON p.SellerID = u.UserID
            """)
        else:
            
            cur.execute("""
                SELECT p.*, u.Username as SellerName
                FROM Products p
                LEFT JOIN Users u ON p.SellerID = u.UserID
            """)
    else:
       
        cur.execute("""
            SELECT p.*, u.Username as SellerName
            FROM Products p
            LEFT JOIN Users u ON p.SellerID = u.UserID
        """)

    rows = cur.fetchall()
    conn.close()

    return render_template("products/products.html", products=rows, user=current_user)

# ---------------------------
# Add a new product
# ---------------------------
@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role not in ("Seller", "Admin"):
        flash("Only sellers or admins can add products.", "danger")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price") or 0)
        stock = int(request.form.get("stock") or 0)
        seller_id = current_user.id if current_user.role == "Seller" else request.form.get("seller_id") or current_user.id

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Products (Name, Price, Stock, SellerID) VALUES (?, ?, ?, ?)",
            (name, price, stock, seller_id)
        )
        conn.commit()
        conn.close()

        flash("Product added successfully!", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/add_product.html")

# ---------------------------
# Update product (price/stock)
# ---------------------------
@products_bp.route("/update/<int:product_id>", methods=["POST"])
@login_required
def update_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Products WHERE ProductID = ?", (product_id,))
    p = cur.fetchone()

    if not p:
        conn.close()
        flash("Product not found.", "danger")
        return redirect(url_for("products.list_products"))

    if current_user.role != "Admin" and p["SellerID"] != current_user.id:
        conn.close()
        flash("Not authorized.", "danger")
        return redirect(url_for("products.list_products"))

    price = request.form.get("price")
    stock = request.form.get("stock")

    try:
        if price is not None and price.strip() != "":
            price_val = float(price)
            cur.execute("UPDATE Products SET Price = ? WHERE ProductID = ?", (price_val, product_id))
        if stock is not None and stock.strip() != "":
            stock_val = int(stock)
            cur.execute("UPDATE Products SET Stock = ? WHERE ProductID = ?", (stock_val, product_id))
    except ValueError:
        conn.close()
        flash("Invalid number entered for price or stock.", "danger")
        return redirect(url_for("products.list_products"))

    conn.commit()
    conn.close()
    flash("Product updated.", "success")
    return redirect(url_for("products.list_products"))
# ---------------------------
# Delete product
# ---------------------------
@products_bp.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Products WHERE ProductID = ?", (product_id,))
    p = cur.fetchone()

    if not p:
        conn.close()
        flash("Product not found.", "danger")
        return redirect(url_for("products.list_products"))

   
    if current_user.role != "Admin" and p["SellerID"] != current_user.id:
        conn.close()
        flash("Not authorized.", "danger")
        return redirect(url_for("products.list_products"))

    cur.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
    conn.commit()
    conn.close()

    flash("Product deleted.", "success")
    return redirect(url_for("products.list_products"))
