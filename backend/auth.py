# backend/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.db import db
from backend.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/admin")


# -------------------------------------------------
# CREATE / FIX DEFAULT ADMIN
# -------------------------------------------------
def create_admin_if_not_exists():
    """
    Ensures a valid admin user always exists.
    Username: admin
    Password: admin123
    """
    admin = User.query.filter_by(username="admin").first()

    hashed_password = generate_password_hash("admin123", method="pbkdf2:sha256")

    if not admin:
        admin = User(
            username="admin",
            password=hashed_password
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created")
    else:
        # 🔧 FIX INVALID HASH
        if not admin.password or ":" not in admin.password:
            admin.password = hashed_password
            db.session.commit()
            print("🔧 Admin password hash repaired")


# -------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = User.query.filter_by(username=username).first()

        if admin:
            try:
                if check_password_hash(admin.password, password):
                    session.clear()
                    session["admin_logged_in"] = True
                    return redirect(url_for("auth.dashboard"))
            except Exception:
                # In case hash is corrupted → repair and retry once
                admin.password = generate_password_hash("admin123")
                db.session.commit()

        return render_template(
            "admin/login.html",
            error="Invalid username or password"
        )

    return render_template("admin/login.html")


# -------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------
@auth_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    return render_template("admin/dashboard.html")


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
