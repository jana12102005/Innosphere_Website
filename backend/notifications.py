# backend/notifications.py

import smtplib
from email.message import EmailMessage
from backend.config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD


def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
