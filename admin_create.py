# create_admin.py

from werkzeug.security import generate_password_hash
from backend.db import db
from backend.models import User
from backend.config import SQLALCHEMY_DATABASE_URI
from flask import Flask

# -------------------------------------------------
# Minimal Flask app for DB access
# -------------------------------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# -------------------------------------------------
# Insert / Fix Admin
# -------------------------------------------------
with app.app_context():
    print("🔧 Fixing admin user...")

    # Remove old admin if exists
    User.query.filter_by(username="admin").delete()

    # Create fresh admin
    admin = User(
        username="admin",
        password=generate_password_hash(
            "admin123",
            method="pbkdf2:sha256"
        )
    )

    db.session.add(admin)
    db.session.commit()

    print("✅ Admin user created successfully")
    print("🔑 Username: admin")
    print("🔑 Password: admin123")
