# backend/candidates.py

from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime

from backend.db import db
from backend.models import Candidate, TeamMember
from backend.notifications import send_email
from backend.cloudinary_helper import upload_file, delete_file

candidates_bp = Blueprint("candidates", __name__)
FOLDER = "innosphere/resumes"


@candidates_bp.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        resume     = request.files.get("resume")
        resume_url = None
        public_id  = None

        if resume and resume.filename:
            result     = upload_file(resume, folder=FOLDER, resource_type="raw")
            resume_url = result["secure_url"]
            public_id  = result["public_id"]

        candidate = Candidate(
            name        = request.form["name"],
            email       = request.form["email"],
            mobile      = request.form.get("mobile"),
            designation = request.form.get("designation"),
            year        = request.form.get("year"),
            college     = request.form.get("college"),
            department  = request.form.get("department"),
            reason      = request.form.get("reason"),
            resume_file          = resume_url,
            cloudinary_public_id = public_id,
            status      = "pending"
        )
        db.session.add(candidate)
        db.session.commit()

        send_email(
            candidate.email,
            "InnoSphere Application Received",
            "Your application has been received. You will be notified after review."
        )
        return redirect(url_for("home"))

    return render_template("join.html")


@candidates_bp.route("/admin/candidates", methods=["GET", "POST"])
def admin_candidates():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # INVITE
        if request.form.get("invite_id"):
            c = Candidate.query.get(int(request.form["invite_id"]))
            c.status         = "invited"
            c.interview_date = request.form.get("interview_date")
            send_email(c.email, "InnoSphere Interview Invitation",
                       f"You are invited for an interview on {c.interview_date}.")

        # ACCEPT → ADD TO TEAM
        if request.form.get("accept_id"):
            c = Candidate.query.get(int(request.form["accept_id"]))
            last = TeamMember.query.filter_by(member_type="member").order_by(TeamMember.id.desc()).first()
            if not last:
                member_id = "PIFINSM001"
            else:
                num = int(last.member_id.replace("PIFINSM", ""))
                member_id = f"PIFINSM{num + 1:03d}"

            member = TeamMember(
                member_id            = member_id,
                name                 = c.name,
                role                 = "Member",
                department           = c.department,
                college              = c.college,
                batch                = c.year,
                member_type          = "member",
                image_file           = None,
                cloudinary_public_id = None,
                created_at           = datetime.utcnow()
            )
            c.status = "accepted"
            db.session.add(member)
            send_email(c.email, "Welcome to InnoSphere 🎉",
                       f"Congratulations {c.name}!\n\nMember ID: {member_id}\n\nWelcome aboard!")

        # REJECT
        if request.form.get("reject_id"):
            c = Candidate.query.get(int(request.form["reject_id"]))
            c.status = "rejected"

        db.session.commit()

    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template("admin/candidates.html", candidates=candidates)
