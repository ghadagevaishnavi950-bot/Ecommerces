from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import config   # import config, not app

users_bp = Blueprint("users", __name__, url_prefix="/users")
DB_PATH = config.DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class User(UserMixin):
    def __init__(self, row):
        self.id = row["UserID"]
        self.username = row["Username"]
        self.password = row["Password"]
        self.email = row["Email"]
        self.role = row["Role"]

    @staticmethod
    def get_by_username(username):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        return User(row) if row else None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return User(row) if row else None

    @staticmethod
    def create(username, password, email, role="Customer"):
        conn = get_db()
        cur = conn.cursor()
        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)",
            (username, hashed, email, role),
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return User.get_by_id(user_id)


# ---------------- Routes ---------------- #

@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role") or "Customer"

        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect(url_for("users.register"))

        if User.get_by_username(username):
            flash("Username already taken.", "danger")
            return redirect(url_for("users.register"))

        User.create(username, password, email, role)
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("users.login"))

    return render_template("users/register.html")


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")
        user = User.get_by_username(username)

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials.", "danger")
            return redirect(url_for("users.login"))

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("users.dashboard"))

    return render_template("users/login.html")


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("users/dashboard.html", user=current_user)
