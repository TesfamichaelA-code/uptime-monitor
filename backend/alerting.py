from datetime import datetime
from email.message import EmailMessage

import aiosmtplib

from config import settings
from models import Target


async def send_email(to_address: str, subject: str, body_text: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        raise RuntimeError("SMTP_USER and SMTP_PASS must be configured")

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body_text)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=587,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
    )


async def notify_initial_status(
    target: Target,
    user_email: str,
    is_up: bool,
    status_code: int = 0,
    checked_at: datetime | None = None,
) -> None:
    timestamp = (checked_at or datetime.utcnow()).isoformat()
    state = "responding" if is_up else "unreachable"
    subject_state = "UP" if is_up else "DOWN"
    body_text = "\n".join(
        [
            f"Initial check: target {target.name} is {state}.",
            f"URL: {target.url}",
            f"Status code: {status_code}",
            f"Timestamp: {timestamp}",
        ]
    )
    await send_email(
        user_email,
        f"{subject_state}: {target.name} initial status is {state}",
        body_text,
    )


async def notify_down(
    target: Target,
    user_email: str,
    status_code: int = 0,
    checked_at: datetime | None = None,
) -> None:
    timestamp = (checked_at or datetime.utcnow()).isoformat()
    body_text = "\n".join(
        [
            f"Target {target.name} is unreachable.",
            f"URL: {target.url}",
            f"Status code: {status_code}",
            f"Timestamp: {timestamp}",
        ]
    )
    await send_email(
        user_email,
        f"DOWN: {target.name} is unreachable",
        body_text,
    )


async def notify_recovery(
    target: Target,
    user_email: str,
    status_code: int = 0,
    checked_at: datetime | None = None,
) -> None:
    timestamp = (checked_at or datetime.utcnow()).isoformat()
    body_text = "\n".join(
        [
            f"Target {target.name} is responding again.",
            f"URL: {target.url}",
            f"Status code: {status_code}",
            f"Timestamp: {timestamp}",
        ]
    )
    await send_email(
        user_email,
        f"BACK UP: {target.name} is responding again",
        body_text,
    )
