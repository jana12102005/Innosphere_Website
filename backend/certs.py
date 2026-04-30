# backend/certs.py
# ─────────────────────────────────────────────────────────────────────────────
#  Certificate system
#  • HTML templates are uploaded to / fetched from Cloudinary  (resource_type=raw)
#  • Generated PDFs are rendered in-memory → streamed to browser  (nothing on disk)
#  • ReportLab draws the full premium certificate natively
#  • Poppins fonts are loaded from the bundled  ./Poppins/  folder
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import io
import requests as http_requests

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session,
    send_file, jsonify
)

from backend.db import db
from backend.models import Event, EventRegistration, CertificateTemplate
from backend.notifications import send_email
from backend.cloudinary_helper import upload_file, delete_file

certs_bp = Blueprint("certs", __name__)

# Poppins fonts live in  <project_root>/Poppins/
_BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FONTS  = os.path.join(_BASE, "Poppins")

# ── Placeholder map ───────────────────────────────────────────────────────────
PLACEHOLDER_MAP = {
    "{{Name}}": "name",   "{{NAME}}": "name",   "{{ NAME }}": "name",
    "{{Department}}": "department", "{{DEPARTMENT}}": "department", "{{ DEPARTMENT }}": "department",
    "{{DEPT}}": "department",       "{{ DEPT }}": "department",     "{{Dept}}": "department",
    "{{College}}":  "college",      "{{COLLEGE}}":  "college",      "{{ COLLEGE }}":  "college",
    "{{Year}}":     "year",         "{{YEAR}}":     "year",         "{{ YEAR }}":     "year",
}


def _fill_template(html_text, reg):
    for placeholder, field in PLACEHOLDER_MAP.items():
        html_text = html_text.replace(placeholder, getattr(reg, field, "") or "")
    return html_text


def _extract_fields(html_content):
    """Pull filled values from the HTML for ReportLab rendering."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    def _t(sel, default=""):
        el = soup.select_one(sel)
        return el.get_text(strip=True) if el else default

    fields = {"name": _t(".recipient-name"), "department": "",
               "college": "", "year": "", "event_title": ""}

    para = soup.select_one(".cert-paragraph")
    if para:
        hl = [e.get_text(strip=True) for e in para.select(".hl")]
        if len(hl) >= 1: fields["department"]  = hl[0]
        if len(hl) >= 2: fields["college"]     = hl[1]
        if len(hl) >= 4: fields["event_title"] = hl[3]

    return fields


# ── Font registration ─────────────────────────────────────────────────────────
def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    fonts = {
        "serif": "Helvetica", "serif_bold": "Helvetica-Bold",
        "serif_italic": "Helvetica-Oblique",
        "sans": "Helvetica", "sans_bold": "Helvetica-Bold",
        "sans_light": "Helvetica", "name_font": "Helvetica-Bold",
    }

    try:
        pdfmetrics.registerFont(TTFont("Poppins",      os.path.join(_FONTS, "Poppins-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("PoppinsBold",  os.path.join(_FONTS, "Poppins-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("PoppinsLight", os.path.join(_FONTS, "Poppins-Light.ttf")))
        pdfmetrics.registerFont(TTFont("PoppinsItalic",os.path.join(_FONTS, "Poppins-Italic.ttf")))
        fonts.update({"sans": "Poppins", "sans_bold": "PoppinsBold",
                      "sans_light": "PoppinsLight", "name_font": "Poppins"})
    except Exception as e:
        print(f"[certs] Font load warning: {e} — falling back to Helvetica")

    return fonts


# ── Certificate drawing ───────────────────────────────────────────────────────
def _draw_certificate(c, w, h, fields, fonts):
    from reportlab.lib.colors import HexColor, white

    NAVY      = HexColor('#0e1f44')
    NAVY_MID  = HexColor('#1a3260')
    GOLD      = HexColor('#b8923a')
    GOLD_L    = HexColor('#f4c430')
    PEARL     = HexColor('#faf8f5')
    SLATE     = HexColor('#4a5568')
    SLATE_L   = HexColor('#718096')
    WHITE     = white

    serif      = fonts["serif"];      serif_bold = fonts["serif_bold"]
    sans       = fonts["sans"];       sans_bold  = fonts["sans_bold"]
    sans_light = fonts["sans_light"]; name_font  = fonts["name_font"]

    # Background
    c.setFillColor(PEARL);  c.rect(0, 0, w, h, fill=1, stroke=0)

    # Outer gold border
    c.setStrokeColor(GOLD); c.setLineWidth(2.5)
    c.rect(8, 8, w-16, h-16, fill=0, stroke=1)

    # Inner border
    c.setStrokeColor(HexColor('#d4a85360')); c.setLineWidth(0.6)
    c.rect(16, 16, w-32, h-32, fill=0, stroke=1)

    # Corner brackets
    bracket = 40; margin = 22
    c.setStrokeColor(GOLD); c.setLineWidth(1.5)
    for (cx, cy, dx, dy) in [
        (margin,   h-margin,  1, -1), (w-margin, h-margin, -1, -1),
        (margin,   margin,    1,  1), (w-margin, margin,   -1,  1),
    ]:
        c.line(cx, cy, cx+dx*bracket, cy)
        c.line(cx, cy, cx, cy+dy*bracket)
        c.setFillColor(GOLD); c.circle(cx, cy, 2.5, fill=1, stroke=0)

    # Dot accents on borders
    c.setFillColor(GOLD_L)
    for x in [w*0.25, w*0.5, w*0.75]:
        c.circle(x, h-8, 1.5, fill=1, stroke=0)
        c.circle(x,   8, 1.5, fill=1, stroke=0)
    for y in [h*0.3, h*0.5, h*0.7]:
        c.circle(8,   y, 1.5, fill=1, stroke=0)
        c.circle(w-8, y, 1.5, fill=1, stroke=0)

    # Navy header trapezoid
    header_h   = 165; header_top = h - header_h - 28; clip_drop = 28
    p = c.beginPath()
    p.moveTo(28, h-28); p.lineTo(w-28, h-28)
    p.lineTo(w-28, header_top+clip_drop); p.lineTo(w/2, header_top)
    p.lineTo(28, header_top+clip_drop); p.close()
    c.setFillColor(NAVY); c.drawPath(p, fill=1, stroke=0)

    # Diagonal stripe texture on header
    c.saveState(); c.clipPath(p, fill=0, stroke=0)
    c.setStrokeColor(HexColor('#b8923a12')); c.setLineWidth(0.5)
    for i in range(-20, int(w/10)+20):
        c.line(28+i*14, h-28, 28+i*14+200, header_top)
    c.restoreState()

    # Header text
    c.setFillColor(HexColor('#ffffff99')); c.setFont(sans_light, 7.5)
    c.drawCentredString(w/2, h-54, "PAAVAI INNOVATION FORUM  ·  PAAVAI ENGINEERING COLLEGE")
    c.setFillColor(GOLD_L); c.setFont(serif_bold, 38)
    c.drawCentredString(w/2, h-90, "CERTIFICATE")
    c.setFillColor(WHITE); c.setFont(sans_light, 13)
    c.drawCentredString(w/2, h-110, "O F   P A R T I C I P A T I O N")

    # Medallion
    med_cx = w/2; med_cy = header_top + clip_drop/2; med_r = 36
    c.setFillColor(WHITE);  c.circle(med_cx, med_cy, med_r+6, fill=1, stroke=0)
    c.setFillColor(GOLD);   c.circle(med_cx, med_cy, med_r+2, fill=1, stroke=0)
    c.setFillColor(HexColor('#c9a44a')); c.circle(med_cx, med_cy, med_r-2, fill=1, stroke=0)
    c.setStrokeColor(HexColor('#0e1f4466')); c.setLineWidth(1)
    c.setDash([3,3]); c.circle(med_cx, med_cy, med_r-8, fill=0, stroke=1); c.setDash([])
    c.setFillColor(NAVY); c.setFont(serif_bold, 8)
    c.drawCentredString(med_cx, med_cy+7,  "INNO")
    c.drawCentredString(med_cx, med_cy-1,  "SPHERE")
    c.setFont(sans, 6.5); c.drawCentredString(med_cx, med_cy-10, "2025")

    # Body
    body_top = med_cy - med_r - 16
    c.setFillColor(SLATE_L); c.setFont(sans, 8.5)
    c.drawCentredString(w/2, body_top-18, "T H I S   I S   T O   C E R T I F Y   T H A T")
    rule_w = 60
    c.setStrokeColor(GOLD); c.setLineWidth(1)
    c.line(w/2-rule_w/2, body_top-28, w/2+rule_w/2, body_top-28)

    # Name
    name = fields.get("name", "Participant")
    c.setFillColor(NAVY); c.setFont(name_font, 34)
    c.drawCentredString(w/2, body_top-60, name)

    # Underline
    uline_y = body_top-70; uline_w = 280
    c.setStrokeColor(GOLD); c.setLineWidth(1.5)
    c.line(w/2-uline_w/2, uline_y, w/2+uline_w/2, uline_y)
    c.setStrokeColor(GOLD_L); c.setLineWidth(0.5)
    c.line(w/2-40, uline_y-3, w/2+40, uline_y-3)

    dept     = fields.get("department", "")
    college  = fields.get("college", "")
    ev_title = fields.get("event_title", "this event")

    text_y = body_top-90
    c.setFont(sans_light, 9.5); c.setFillColor(SLATE)
    c.drawCentredString(w/2, text_y, f"of  {dept}  from  {college}")
    text_y -= 16
    c.drawCentredString(w/2, text_y, "has successfully participated in a  1-Day Workshop  titled")
    text_y -= 16
    c.setFont(sans_bold, 9.5); c.setFillColor(NAVY)
    c.drawCentredString(w/2, text_y, f'"{ev_title}"')
    text_y -= 14
    c.setFont(sans_light, 9.5); c.setFillColor(SLATE)
    c.drawCentredString(w/2, text_y, "conducted by  InnoSphere Club,  Paavai Innovation Forum.")

    # Divider
    div_y = text_y-22; div_w = 200
    c.setStrokeColor(HexColor('#b8923a88')); c.setLineWidth(0.6)
    c.line(w/2-div_w, div_y, w/2-8, div_y); c.line(w/2+8, div_y, w/2+div_w, div_y)
    c.setFillColor(GOLD)
    c.saveState(); c.translate(w/2, div_y); c.rotate(45)
    c.rect(-4,-4,8,8,fill=1,stroke=0); c.restoreState()

    # Signatures
    sig_y    = div_y-16
    sig_data = [
        ("Ms. Kamala KrishnaMurthy", "Head\nPaavai Innovation Forum"),
        ("Dr. R. R. Krishnamurthy",  "Director\nPaavai Innovation Forum"),
        ("Dr. M. Premkumar",         "Principal\nPaavai Engineering College"),
    ]
    col_w = (w-80) / len(sig_data)
    for i, (name_s, title_s) in enumerate(sig_data):
        cx_s  = 40 + col_w*i + col_w/2
        line_y = sig_y - 42
        c.setStrokeColor(GOLD); c.setLineWidth(0.8)
        c.line(cx_s-55, line_y, cx_s+55, line_y)
        c.setFillColor(NAVY);   c.setFont(sans_bold, 7.5)
        c.drawCentredString(cx_s, line_y-11, name_s)
        c.setFillColor(SLATE_L); c.setFont(sans_light, 7)
        for j, tline in enumerate(title_s.split("\n")):
            c.drawCentredString(cx_s, line_y-20-j*9, tline)

    # Footer strip
    c.setFillColor(NAVY); c.rect(28, 28, w-56, 22, fill=1, stroke=0)
    c.setFillColor(GOLD); c.setFont(sans_bold, 6.5)
    c.drawString(40, 36, "InnoSphere")
    c.setFillColor(HexColor('#ffffff66')); c.setFont(sans_light, 6.5)
    c.drawString(96, 36, "·  Paavai Innovation Forum")
    c.drawRightString(w-40, 36, "Paavai Engineering College, Namakkal")


# ── PDF generator — fully in-memory ──────────────────────────────────────────
def _generate_pdf_buffer(html_content):
    """
    Returns (BytesIO_buffer, None) on success or (None, error_str) on failure.
    Everything is kept in RAM — nothing written to disk.
    """
    # Try WeasyPrint first (best quality)
    try:
        from weasyprint import HTML as WP_HTML
        buf = io.BytesIO()
        WP_HTML(string=html_content).write_pdf(buf)
        buf.seek(0)
        return buf, None
    except ImportError:
        pass
    except Exception:
        pass

    # Fall back to ReportLab native renderer
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.pdfgen import canvas as rl_canvas

        fields = _extract_fields(html_content)
        fonts  = _register_fonts()
        w, h   = landscape(A4)

        buf = io.BytesIO()
        c   = rl_canvas.Canvas(buf, pagesize=landscape(A4))
        c.setTitle("Certificate of Participation")
        c.setAuthor("InnoSphere Club")
        _draw_certificate(c, w, h, fields, fonts)
        c.save()
        buf.seek(0)
        return buf, None

    except Exception as e:
        return None, str(e)


# ── ADMIN: upload / delete certificate templates ──────────────────────────────
@certs_bp.route("/admin/certificates", methods=["GET", "POST"])
def admin_certificates():
    if not session.get("admin_logged_in"):
        return redirect(url_for("auth.login"))

    msg = err = None

    if request.method == "POST":

        # DELETE
        if request.form.get("delete_id"):
            tmpl = CertificateTemplate.query.get(request.form["delete_id"])
            if tmpl:
                # getattr guards against the column not yet being migrated
                pub_id = getattr(tmpl, "cloudinary_public_id", None)
                delete_file(pub_id, resource_type="raw")
                db.session.delete(tmpl)
                db.session.commit()
                msg = "Template deleted."
            return redirect(url_for("certs.admin_certificates"))

        # UPLOAD
        event_title = request.form.get("event_title", "").strip()
        html_file   = request.files.get("template")

        if not event_title or not html_file or not html_file.filename:
            err = "Event title and HTML template are both required."
        else:
            # Validate placeholders before upload
            content = html_file.read().decode("utf-8", errors="ignore")
            html_file.seek(0)               # reset stream for upload

            if not any(ph in content for ph in PLACEHOLDER_MAP):
                err = ("Warning: no recognized placeholders found. "
                       "Use {{Name}}, {{Department}}, {{College}}, {{Year}}.")

            # Upload HTML as raw to Cloudinary
            result = upload_file(html_file, folder="innosphere/cert_templates", resource_type="raw")
            tmpl   = CertificateTemplate(
                event_title          = event_title,
                ppt_template_file    = result["secure_url"],
                cloudinary_public_id = result["public_id"],
            )
            db.session.add(tmpl)
            db.session.commit()
            msg = f"Template uploaded for event '{event_title}'."

    templates = CertificateTemplate.query.order_by(CertificateTemplate.created_at.desc()).all()
    events    = Event.query.order_by(Event.title).all()
    return render_template("admin/certificates.html",
                           templates=templates, events=events, msg=msg, err=err)


# ── PUBLIC: certificate download page ────────────────────────────────────────
@certs_bp.route("/certificate", methods=["GET", "POST"])
def certificate():
    templates    = CertificateTemplate.query.all()
    event_titles = [t.event_title for t in templates]
    error = success_data = None

    if request.method == "POST":
        email          = (request.form.get("email") or "").strip().lower()
        selected_event = (request.form.get("event_title") or "").strip()

        if not email:
            error = "Please enter your registered email address."
        elif not selected_event:
            error = "Please select an event."
        else:
            tmpl = CertificateTemplate.query.filter_by(event_title=selected_event).first()
            if not tmpl:
                error = "Certificate template not found for this event."
            else:
                reg = (
                    EventRegistration.query
                    .join(Event, isouter=True)
                    .filter(EventRegistration.email.ilike(email),
                            Event.title == selected_event)
                    .first()
                )
                if not reg:
                    error = ("No registration found. "
                             "Use the same email you registered with.")
                else:
                    # ── Fetch HTML template from Cloudinary ──
                    try:
                        resp    = http_requests.get(tmpl.ppt_template_file, timeout=12)
                        html_src = resp.text
                    except Exception as e:
                        error = f"Could not fetch certificate template: {e}"
                        return render_template("certificate.html",
                                               event_titles=event_titles, error=error)

                    html_filled = _fill_template(html_src, reg)

                    buf, gen_err = _generate_pdf_buffer(html_filled)
                    if buf:
                        send_email(reg.email, "Your Certificate – InnoSphere",
                                   "Your certificate has been generated successfully.")
                        safe = re.sub(r"[^\w]", "_", f"{selected_event}_{reg.name}")
                        return send_file(
                            buf,
                            mimetype      = "application/pdf",
                            as_attachment = False,
                            download_name = f"certificate_{safe}.pdf",
                        )
                    else:
                        error = f"PDF generation failed: {gen_err}"

    return render_template("certificate.html",
                           event_titles=event_titles, error=error, success=success_data)


# ── AJAX: smart event dropdown ────────────────────────────────────────────────
@certs_bp.route("/certificate/lookup", methods=["POST"])
def certificate_lookup():
    email = (request.get_json(silent=True) or {}).get("email", "").strip().lower()
    if not email:
        return jsonify({"events": []})

    regs = (EventRegistration.query.join(Event, isouter=True)
            .filter(EventRegistration.email.ilike(email)).all())

    template_titles = {t.event_title for t in CertificateTemplate.query.all()}
    events, seen    = [], set()
    for r in regs:
        title = r.event.title if r.event else None
        if title and title in template_titles and title not in seen:
            events.append(title); seen.add(title)

    return jsonify({"events": events})