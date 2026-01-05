import secrets
from datetime import datetime, timedelta, timezone
from .database import SessionLocal
from .models import EmailToken
from sqlalchemy.exc import IntegrityError

TOKEN_TTL_MINUTES = 60 * 24  # 24 hours by default


def generate_email_token(author: str, ttl_minutes: int = TOKEN_TTL_MINUTES) -> str:
    db = SessionLocal()
    try:
        raw = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        et = EmailToken(token=raw, author=author, expires_at=expires, used=0)
        db.add(et)
        db.commit()
        return raw
    except IntegrityError:
        db.rollback()
        return generate_email_token(author, ttl_minutes)
    finally:
        db.close()


def consume_email_token(token: str) -> str | None:
    """Mark token as used and return author if valid; otherwise return None."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        t = db.query(EmailToken).filter_by(token=token).first()
        if not t:
            return None
        if t.used:
            return None
        # normalize expires_at: some DB backends (sqlite) may return naive datetimes
        expires = t.expires_at
        if expires.tzinfo is None:
            from datetime import timezone as _tz

            expires = expires.replace(tzinfo=_tz.utc)
        if expires < now:
            return None
        t.used = 1
        db.add(t)
        db.commit()
        return t.author
    finally:
        db.close()


def validate_email_token(token: str) -> str | None:
    """Validate token without consuming it. Return author if valid, otherwise None."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        t = db.query(EmailToken).filter_by(token=token).first()
        if not t:
            return None
        if t.used:
            return None
        expires = t.expires_at
        if expires.tzinfo is None:
            from datetime import timezone as _tz

            expires = expires.replace(tzinfo=_tz.utc)
        if expires < now:
            return None
        return t.author
    finally:
        db.close()