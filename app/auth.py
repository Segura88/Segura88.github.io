import os
import hmac
import hashlib
import base64
from .config import AUTHORS

SECRET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".secret")


def _load_or_create_secret() -> bytes:
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "rb") as f:
            return f.read().strip()
    # create a random secret
    s = os.urandom(32)
    with open(SECRET_FILE, "wb") as f:
        f.write(s)
    return s


SECRET = _load_or_create_secret()


def generate_token(author: str) -> str:
    # payload is author (A or B)
    payload = author.encode("utf-8")
    sig = hmac.new(SECRET, payload, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(payload + b":" + sig).decode("ascii")
    return token


def verify_token(token: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii"))
        payload, sig = raw.split(b":", 1)
        expected = hmac.new(SECRET, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, sig):
            raise ValueError("invalid signature")
        author = payload.decode("utf-8")
        if author not in AUTHORS:
            raise ValueError("invalid author")
        return author
    except Exception:
        raise
