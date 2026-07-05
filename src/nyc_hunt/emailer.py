"""Optional SMTP digest. Password only from env NYC_HUNT_SMTP_PASS — never config."""
import os
import smtplib
from email.mime.text import MIMEText

from .config import Email


class EmailError(Exception):
    pass


def send(cfg: Email, subject: str, html: str) -> None:
    password = os.environ.get("NYC_HUNT_SMTP_PASS")
    if not (cfg.enabled and cfg.to and cfg.smtp_user and password):
        raise EmailError("email not configured (enabled/to/smtp_user/NYC_HUNT_SMTP_PASS)")
    msg = MIMEText(html, "html")
    msg["Subject"], msg["From"], msg["To"] = subject, cfg.smtp_user, cfg.to
    try:
        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as s:
            s.starttls()
            s.login(cfg.smtp_user, password)
            s.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        raise EmailError(str(e)) from e
