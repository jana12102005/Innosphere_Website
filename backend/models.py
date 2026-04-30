# backend/models.py

from datetime import datetime
from backend.db import db


# ============================
# ADMIN USERS
# ============================
class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(100), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================
# JOIN US – CANDIDATES
# ============================
class Candidate(db.Model):
    __tablename__ = "candidates"
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(200), nullable=False)
    email          = db.Column(db.String(200), nullable=False)
    mobile         = db.Column(db.String(20))
    designation    = db.Column(db.String(100))
    year           = db.Column(db.String(20))
    college        = db.Column(db.String(200))
    department     = db.Column(db.String(200))
    resume_file    = db.Column(db.String(500))   # Cloudinary URL
    cloudinary_public_id = db.Column(db.String(500))
    reason         = db.Column(db.Text)
    status         = db.Column(db.String(20), default="pending")
    interview_date = db.Column(db.String(50))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)


# ============================
# EVENTS
# ============================
class Event(db.Model):
    __tablename__ = "events"
    id                   = db.Column(db.Integer, primary_key=True)
    title                = db.Column(db.String(255), nullable=False)
    description          = db.Column(db.Text)
    brochure_file        = db.Column(db.String(500))   # Cloudinary URL
    cloudinary_public_id = db.Column(db.String(500))
    dynamic_fields       = db.Column(db.Text)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)


# ============================
# EVENT REGISTRATIONS
# ============================
class EventRegistration(db.Model):
    __tablename__ = "event_registrations"
    id            = db.Column(db.Integer, primary_key=True)
    event_id      = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name          = db.Column(db.String(200), nullable=False)
    email         = db.Column(db.String(200), nullable=False)
    department    = db.Column(db.String(200))
    college       = db.Column(db.String(200))
    year          = db.Column(db.String(50))
    contact       = db.Column(db.String(50))
    extra_answers = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    event         = db.relationship(
        "Event",
        backref=db.backref("registrations", lazy=True, passive_deletes=True)
    )


# ============================
# PROJECT <-> MEMBER JOIN TABLE
# ============================
project_members = db.Table(
    "project_members",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id",     ondelete="CASCADE"), primary_key=True),
    db.Column("member_id",  db.Integer, db.ForeignKey("team_members.id", ondelete="CASCADE"), primary_key=True)
)


# ============================
# PROJECTS
# ============================
class Project(db.Model):
    __tablename__ = "projects"
    id                   = db.Column(db.Integer, primary_key=True)
    title                = db.Column(db.String(255), nullable=False)
    description          = db.Column(db.Text)
    image_file           = db.Column(db.String(500))   # Cloudinary URL
    cloudinary_public_id = db.Column(db.String(500))
    status               = db.Column(db.String(20), default="ongoing", nullable=False)
    lead_id              = db.Column(db.Integer, db.ForeignKey("team_members.id", ondelete="SET NULL"), nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    lead                 = db.relationship("TeamMember", foreign_keys=[lead_id], backref=db.backref("led_projects", lazy=True))
    members              = db.relationship("TeamMember", secondary=project_members, backref=db.backref("projects", lazy=True), lazy=True)


# ============================
# CERTIFICATE TEMPLATES
# ============================
class CertificateTemplate(db.Model):
    __tablename__ = "cert_templates"
    id                   = db.Column(db.Integer, primary_key=True)
    event_title          = db.Column(db.String(255), nullable=False)
    ppt_template_file    = db.Column(db.String(500), nullable=False)
    cloudinary_public_id = db.Column(db.String(500), nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)


# ============================
# GALLERY
# ============================
class GalleryImage(db.Model):
    __tablename__ = "gallery_images"
    id                   = db.Column(db.Integer, primary_key=True)
    title                = db.Column(db.String(255))
    image_file           = db.Column(db.String(500))   # Cloudinary URL
    cloudinary_public_id = db.Column(db.String(500))
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)


# ============================
# DEFAULT OFFICE BEARER ROLES
# ============================
DEFAULT_OFFICE_ROLES = [
    "President", "Vice President", "Secretary", "Joint Secretary", "CTO",
    "IT Wing 1", "IT Wing 2", "IT Wing 3", "IT Wing 4",
    "IT Wing 5", "IT Wing 6", "IT Wing 7",
    "Event Coordinator 1",  "Event Coordinator 2",  "Event Coordinator 3",
    "Event Coordinator 4",  "Event Coordinator 5",  "Event Coordinator 6",
    "Event Coordinator 7",  "Event Coordinator 8",  "Event Coordinator 9",
    "Event Coordinator 10", "Event Coordinator 11", "Event Coordinator 12",
    "Event Coordinator 13", "Event Coordinator 14", "Event Coordinator 15",
]


# ============================
# TEAM MEMBERS
# ============================
class TeamMember(db.Model):
    __tablename__ = "team_members"
    id                   = db.Column(db.Integer, primary_key=True)
    member_id            = db.Column(db.String(20), unique=True, nullable=False)
    name                 = db.Column(db.String(200), nullable=False)
    role                 = db.Column(db.String(100))
    department           = db.Column(db.String(200))
    college              = db.Column(db.String(200))
    batch                = db.Column(db.String(50))
    member_type          = db.Column(db.String(20), nullable=False)   # office | member
    image_file           = db.Column(db.String(500))                  # Cloudinary URL
    cloudinary_public_id = db.Column(db.String(500))
    is_former            = db.Column(db.Boolean, default=False, nullable=False)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)