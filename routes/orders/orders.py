from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")
DB_PATH = "ecommerce.db"

# ---------------------------
# Database connection
# ---------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# Place Order (for Customer)
# ---------------------------
@orders_bp.route("/place/<int:product_id>", methods=["POST"])
@login_required
def place_order(product_id):
    if getattr(current_user, "role", "") != "Customer":
        flash("Only customers can place orders.", "danger")
        return redirect(url_for("products.list_products"))

    quantity = request.form.get("quantity", 1)
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash("Invalid quantity.", "danger")
        return redirect(url_for("products.list_products"))

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Products WHERE ProductID = ?", (product_id,))
        product = cur.fetchone()
        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("products.list_products"))

        if product["Stock"] < quantity:
            flash("Not enough stock available.", "danger")
            return redirect(url_for("products.list_products"))

        # Update stock
        new_stock = product["Stock"] - quantity
        cur.execute("UPDATE Products SET Stock=? WHERE ProductID=?", (new_stock, product_id))

        # Insert order
        cur.execute(
            "INSERT INTO Orders (UserID, ProductID, Quantity) VALUES (?, ?, ?)",
            (current_user.id, product_id, quantity)
        )

        conn.commit()
        flash(f"Order placed: {quantity} x {product['Name']}", "success")
    except Exception as e:
        flash(f"Error placing order: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("products.list_products"))


# ---------------------------
@orders_bp.route("/myorders")
@login_required
def my_orders():
    conn = get_db()
    cur = conn.cursor()

    if current_user.role == "Admin":
        # Admin -> 
        cur.execute("""
            SELECT Orders.OrderID, Orders.Quantity, Orders.OrderDate,
                   Products.Name AS ProductName,
                   U1.Username AS Buyer,
                   U2.Username AS Seller
            FROM Orders
            JOIN Users U1 ON Orders.UserID = U1.UserID
            JOIN Products ON Orders.ProductID = Products.ProductID
            LEFT JOIN Users U2 ON Products.SellerID = U2.UserID
            ORDER BY Orders.OrderDate DESC
        """)
    elif current_user.role == "Seller":
        # Seller ->
        cur.execute("""
            SELECT Orders.OrderID, Orders.Quantity, Orders.OrderDate,
                   Products.Name AS ProductName,
                   U1.Username AS Buyer,
                   U2.Username AS Seller
            FROM Orders
            JOIN Users U1 ON Orders.UserID = U1.UserID
            JOIN Products ON Orders.ProductID = Products.ProductID
            LEFT JOIN Users U2 ON Products.SellerID = U2.UserID
            WHERE Products.SellerID = ?
            ORDER BY Orders.OrderDate DESC
        """, (current_user.id,))
    else:
        # Customer -> 
        cur.execute("""
            SELECT Orders.OrderID, Orders.Quantity, Orders.OrderDate,
                   Products.Name AS ProductName,
                   U1.Username AS Buyer,
                   U2.Username AS Seller
            FROM Orders
            JOIN Users U1 ON Orders.UserID = U1.UserID
            JOIN Products ON Orders.ProductID = Products.ProductID
            LEFT JOIN Users U2 ON Products.SellerID = U2.UserID
            WHERE Orders.UserID = ?
            ORDER BY Orders.OrderDate DESC
        """, (current_user.id,))

    orders = cur.fetchall()
    conn.close()
    return render_template("orders/myorders.html", orders=orders)