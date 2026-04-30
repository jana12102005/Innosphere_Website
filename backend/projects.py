# backend/projects.py

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.db import db
from backend.models import Project, TeamMember, project_members
from backend.cloudinary_helper import upload_file, delete_file

projects_bp = Blueprint("projects", __name__)
FOLDER = "innosphere/projects"


@projects_bp.route("/projects")
def projects_list():
    ongoing   = Project.query.filter_by(status="ongoing").order_by(Project.created_at.desc()).all()
    completed = Project.query.filter_by(status="completed").order_by(Project.created_at.desc()).all()
    return render_template("projects.html", ongoing=ongoing, completed=completed)


@projects_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)


@projects_bp.route("/admin/projects", methods=["GET", "POST"])
def admin_projects():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # ── DELETE ──────────────────────────────────
        if request.form.get("delete_id"):
            p = Project.query.get(request.form["delete_id"])
            if p:
                delete_file(getattr(p, "cloudinary_public_id", None), resource_type="image")
                db.session.delete(p)
                db.session.commit()
            return redirect(url_for("projects.admin_projects"))

        # ── TOGGLE STATUS ────────────────────────────
        if request.form.get("toggle_id"):
            p = Project.query.get(request.form["toggle_id"])
            if p:
                p.status = "completed" if p.status == "ongoing" else "ongoing"
                db.session.commit()
            return redirect(url_for("projects.admin_projects"))

        # ── ADD MEMBER TO PROJECT ────────────────────
        if request.form.get("add_member_project_id"):
            p = Project.query.get(request.form["add_member_project_id"])
            m = TeamMember.query.get(request.form["add_member_id"])
            if p and m and m not in p.members:
                p.members.append(m)
                db.session.commit()
            return redirect(url_for("projects.admin_projects"))

        # ── CREATE PROJECT ───────────────────────────
        image_url = None
        public_id = None
        image = request.files.get("image")
        if image and image.filename:
            result    = upload_file(image, folder=FOLDER, resource_type="image")
            image_url = result["secure_url"]
            public_id = result["public_id"]

        lead_id    = request.form.get("lead_id") or None
        member_ids = request.form.getlist("member_ids")

        project = Project(
            title                = request.form.get("title", "").strip(),
            description          = request.form.get("description", "").strip(),
            status               = request.form.get("status", "ongoing"),
            lead_id              = int(lead_id) if lead_id else None,
            image_file           = image_url,
            cloudinary_public_id = public_id,
        )
        db.session.add(project)
        db.session.flush()

        for mid in member_ids:
            m = TeamMember.query.get(int(mid))
            if m:
                project.members.append(m)

        db.session.commit()
        return redirect(url_for("projects.admin_projects"))

    projects    = Project.query.order_by(Project.created_at.desc()).all()
    all_members = TeamMember.query.filter_by(is_former=False).order_by(TeamMember.name).all()
    return render_template("admin/projects.html", projects=projects, all_members=all_members)
