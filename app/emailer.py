from email.message import EmailMessage
import smtplib
import os
from typing import Optional
from .config import (
    EMAILS_ENABLED,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
    EMAIL_FROM,
    EMAIL_RECIPIENTS,
    RESEND_API_KEY,
    RESEND_FROM,
)
import requests


def send_email(subject: str, body: str, to: str) -> bool:
    """Send a simple plain-text email. Returns True on success, False otherwise.

    This function is safe to call even when EMAILS_ENABLED is False — it will
    only log/skip sending.
    """
    if not EMAILS_ENABLED:
        # In dev the caller can log or mock this call — don't raise.
        print(f"[emailer] EMAILS_ENABLED is False, skipping send to {to}: {subject}")
        return False

    if not SMTP_HOST and not RESEND_API_KEY:
        print("[emailer] SMTP_HOST not configured, skipping send")
        return False

    # Prefer Resend if configured.
    if RESEND_API_KEY:
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": RESEND_FROM,
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
                timeout=10,
            )
            if 200 <= resp.status_code < 300:
                return True
            print(f"[emailer] Resend error {resp.status_code}: {resp.text}")
            return False
        except Exception as e:
            print(f"[emailer] Resend exception: {e}")
            return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    msg.set_content(body)

    password = os.environ.get("SMTP_PASSWORD")
    try:
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                s.starttls()
                if SMTP_USER and password:
                    s.login(SMTP_USER, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                if SMTP_USER and password:
                    s.login(SMTP_USER, password)
                s.send_message(msg)
        return True
    except Exception as e:
        print(f"[emailer] Error sending email to {to}: {e}")
        return False
