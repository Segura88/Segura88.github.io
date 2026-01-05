from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import verify_token
from .tokens import consume_email_token
from .config import AUTHORS

security = HTTPBearer(auto_error=False)


def get_author(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing token")
    token = credentials.credentials
    try:
        # First try HMAC-signed persistent tokens
        try:
            author = verify_token(token)
            if author not in AUTHORS:
                raise HTTPException(status_code=401, detail="Invalid token")
            return author
        except Exception:
            # Not a HMAC token — try consuming a DB-backed single-use token
            author = consume_email_token(token)
            if not author:
                raise HTTPException(status_code=401, detail="Invalid token")
            if author not in AUTHORS:
                raise HTTPException(status_code=401, detail="Invalid token")
            return author
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
