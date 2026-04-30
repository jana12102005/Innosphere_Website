# backend/gallery.py

from flask import Blueprint, render_template, request, redirect, url_for, session
from backend.db import db
from backend.models import GalleryImage
from backend.cloudinary_helper import upload_file, delete_file

gallery_bp = Blueprint("gallery", __name__)
FOLDER = "innosphere/gallery"


@gallery_bp.route("/gallery")
def public_gallery():
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template("gallery.html", images=images)


@gallery_bp.route("/admin/gallery", methods=["GET", "POST"])
def admin_gallery():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        delete_id = request.form.get("delete_id")
        if delete_id:
            img = GalleryImage.query.get(delete_id)
            if img:
                delete_file(getattr(img, "cloudinary_public_id", None), resource_type="image")
                db.session.delete(img)
                db.session.commit()
            return redirect(url_for("gallery.admin_gallery"))

        image = request.files.get("image")
        title = request.form.get("title", "")
        if image and image.filename:
            result = upload_file(image, folder=FOLDER, resource_type="image")
            g = GalleryImage(
                title                = title,
                image_file           = result["secure_url"],
                cloudinary_public_id = result["public_id"],
            )
            db.session.add(g)
            db.session.commit()

    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template("admin/gallery.html", images=images)
