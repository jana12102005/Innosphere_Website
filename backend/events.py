# backend/events.py

import json
import csv
from io import StringIO

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, Response
)
from sqlalchemy import distinct

from backend.db import db
from backend.models import Event, EventRegistration
from backend.notifications import send_email
from backend.cloudinary_helper import upload_file, delete_file

events_bp = Blueprint("events", __name__)
FOLDER = "innosphere/events"


@events_bp.route("/events")
def events_list():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("events.html", events=events)


@events_bp.route("/events/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
    event  = Event.query.get_or_404(event_id)
    fields = json.loads(event.dynamic_fields) if event.dynamic_fields else []

    if request.method == "POST":
        answers = {f: request.form.get(f) for f in fields}
        reg = EventRegistration(
            event_id     = event.id,
            name         = request.form.get("name"),
            email        = request.form.get("email"),
            department   = request.form.get("department"),
            college      = request.form.get("college"),
            year         = request.form.get("year"),
            contact      = request.form.get("contact"),
            extra_answers = json.dumps(answers)
        )
        db.session.add(reg)
        db.session.commit()
        send_email(reg.email, f"{event.title} Registration Confirmed",
                   "Thank you for registering for the event.")
        return render_template("event_detail.html", event=event, dynamic_fields=fields, success=True)

    return render_template("event_detail.html", event=event, dynamic_fields=fields)


@events_bp.route("/admin/events", methods=["GET", "POST"])
def admin_events():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        # DELETE
        delete_id = request.form.get("delete_id")
        if delete_id:
            event = Event.query.get(delete_id)
            if event:
                delete_file(getattr(event, "cloudinary_public_id", None), resource_type="raw")
                db.session.delete(event)
                db.session.commit()
            return redirect(url_for("events.admin_events"))

        # CREATE
        brochure     = request.files.get("brochure")
        brochure_url = None
        public_id    = None

        if brochure and brochure.filename:
            result       = upload_file(brochure, folder=FOLDER, resource_type="auto")
            brochure_url = result["secure_url"]
            public_id    = result["public_id"]

        fields = request.form.getlist("field_name")
        event  = Event(
            title                = request.form.get("title"),
            description          = request.form.get("description"),
            brochure_file        = brochure_url,
            cloudinary_public_id = public_id,
            dynamic_fields       = json.dumps(fields)
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for("events.admin_events"))

    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("admin/events.html", events=events)


@events_bp.route("/admin/participants")
def admin_participants():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    event_id   = request.args.get("event_id")
    college    = request.args.get("college")
    department = request.args.get("department")
    year       = request.args.get("year")

    query = EventRegistration.query.join(Event)
    if event_id:   query = query.filter(Event.id == event_id)
    if college:    query = query.filter(EventRegistration.college == college)
    if department: query = query.filter(EventRegistration.department == department)
    if year:       query = query.filter(EventRegistration.year == year)

    registrations = query.order_by(EventRegistration.created_at.desc()).all()
    events        = Event.query.all()
    colleges      = db.session.query(distinct(EventRegistration.college)).all()
    departments   = db.session.query(distinct(EventRegistration.department)).all()
    years         = db.session.query(distinct(EventRegistration.year)).all()

    return render_template(
        "admin/participants.html",
        registrations = registrations,
        events        = events,
        colleges      = [c[0] for c in colleges if c[0]],
        departments   = [d[0] for d in departments if d[0]],
        years         = [y[0] for y in years if y[0]],
        total         = len(registrations)
    )


@events_bp.route("/admin/participants/export")
def export_participants_csv():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))
    query  = EventRegistration.query.join(Event).all()
    si     = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Event", "Name", "Email", "Department", "College", "Year", "Contact"])
    for r in query:
        writer.writerow([r.event.title, r.name, r.email, r.department, r.college, r.year, r.contact])
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=participants.csv"})
