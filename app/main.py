from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse

from .database import SessionLocal, engine
from .models import Base, WeeklyMemory
from .schemas import WeeklyMemoryCreate, WeeklyMemoryOut
from .schemas import GoalCreate, GoalOut, UnlinkedCreate, UnlinkedOut
from . import time
from .deps import get_author
try:
    from .scheduler import start as scheduler_start, stop as scheduler_stop
except Exception:
    scheduler_start = None
    scheduler_stop = None
from .tokens import consume_email_token, validate_email_token
from fastapi.responses import JSONResponse, RedirectResponse
from .config import EXTERNAL_BASE_URL, AUTHORS, EMAIL_RECIPIENTS
from .config import ADMIN_USER, ADMIN_PASSWORD_HASH
from .emailer import send_email
from passlib.context import CryptContext
import jwt
from datetime import timedelta

# Use the same SECRET as other HMAC tokens for signing admin JWTs
from .auth import SECRET, generate_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_jwt(username: str):
    payload = {"sub": username}
    # short expiry for admin tokens — 1 hour
    payload["exp"] = (time.now()).timestamp() + 3600
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return token


def verify_admin_jwt(token: str):
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        sub = data.get("sub")
        import os
        admin_user = ADMIN_USER or os.environ.get("ADMIN_USER")
        if sub and admin_user and sub == admin_user:
            return True
        return False
    except Exception:
        return False



Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    if scheduler_start:
        scheduler_start()
    yield
    # shutdown
    if scheduler_stop:
        scheduler_stop()


app = FastAPI(lifespan=lifespan)

# Allow frontend dev origins (React/Vite, etc.)
app.add_middleware(
    CORSMiddleware,
    # development origins: include common Vite ports (5173/5174) on localhost and 127.0.0.1
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://segurarodrigue.me",
        "https://www.segurarodrigue.me",
        "https://segura88.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/weekly-memory", response_model=WeeklyMemoryOut)
def create_weekly_memory(
    payload: WeeklyMemoryCreate,
    db: Session = Depends(get_db),
    author: str = Depends(get_author),
    request: Request = None,
):
    # Allow tests to override current time via X-TEST-NOW header (ISO format)
    current = time.now()
    if request is not None:
        test_now = request.headers.get("x-test-now")
        if test_now:
            try:
                dt = datetime.fromisoformat(test_now)
                # normalize to configured TZ
                from . import time as _time

                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_time.TZ)
                else:
                    dt = dt.astimezone(_time.TZ)
                current = dt
            except Exception:
                # ignore parse errors and use real now()
                pass

    if not time.can_write(current):
        raise HTTPException(status_code=403, detail="Not writable now")

    monday = time.week_monday(current)

    # Check if THIS AUTHOR already has a memory for this week
    existing = db.query(WeeklyMemory).filter_by(week_monday=monday, author=author).first()
    if existing:
        # Update existing memory
        existing.text = payload.text
        existing.updated_at = current
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new memory for this author
    memory = WeeklyMemory(
        week_monday=monday,
        text=payload.text,
        author=author,
        created_at=current,
        updated_at=current,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


# NOTE: development-only token generation endpoint removed for security.

@app.get("/weeks")
def get_weeks(db: Session = Depends(get_db)):
    weeks = time.all_2026_weeks()
    all_memories = db.query(WeeklyMemory).all()
    
    # Group memories by week
    memories_by_week = {}
    for m in all_memories:
        if m.week_monday not in memories_by_week:
            memories_by_week[m.week_monday] = []
        memories_by_week[m.week_monday].append(m)

    result = []
    for w in weeks:
        if w in memories_by_week:
            # Multiple authors may have written for this week
            week_memories = memories_by_week[w]
            result.append({
                "week_monday": w.isoformat(),
                "status": "written",
                "memories": [
                    {
                        "author": m.author,
                        "text": m.text,
                        "created_at": m.created_at.isoformat(),
                        "updated_at": m.updated_at.isoformat(),
                    }
                    for m in week_memories
                ],
            })
        else:
            result.append({
                "week_monday": w.isoformat(),
                "status": "pending",
            })
    return result



@app.get("/token/{token}")
def consume_token(token: str):
    # Validate without consuming: this endpoint is used by the frontend to check token validity
    author = validate_email_token(token)
    if not author:
        return JSONResponse(status_code=404, content={"detail": "invalid or expired token"})
    # If EXTERNAL_BASE_URL is configured, redirect to frontend with the token.
    if EXTERNAL_BASE_URL:
        redirect_to = f"{EXTERNAL_BASE_URL.rstrip('/')}/write?token={token}&author={author}"
        return RedirectResponse(url=redirect_to)

    # Otherwise return author — frontend can accept this response and allow writing
    return {"author": author, "ok": True}


from pydantic import BaseModel


class AdminLogin(BaseModel):
    username: str
    password: str


@app.post("/admin/login")
def admin_login(payload: AdminLogin):
    # Read admin config from environment at request time to handle reloads
    import os
    admin_user = ADMIN_USER or os.environ.get("ADMIN_USER")
    admin_hash = ADMIN_PASSWORD_HASH or os.environ.get("ADMIN_PASSWORD_HASH")
    if not admin_user or not admin_hash:
        raise HTTPException(status_code=503, detail="Admin not configured")

    if payload.username != admin_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # verify password
    if not pwd_context.verify(payload.password, admin_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_admin_jwt(payload.username)
    return {"ok": True, "token": token}


@app.get("/admin/ping")
def admin_ping(authorization: str | None = None):
    # Accept Authorization: Bearer <token>
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = parts[1]
    # ensure admin user is read dynamically as well
    import os
    admin_user = ADMIN_USER or os.environ.get("ADMIN_USER")
    if not admin_user:
        raise HTTPException(status_code=503, detail="Admin not configured")
    if not verify_admin_jwt(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"ok": True}


@app.post("/admin/send-test-emails")
def admin_send_test_emails(request: Request):
    # Authorization: Bearer <token>
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = parts[1]
    if not verify_admin_jwt(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    base_url = (EXTERNAL_BASE_URL or "").rstrip("/")
    if not base_url:
        raise HTTPException(status_code=400, detail="EXTERNAL_BASE_URL not configured")

    results = []
    for author in AUTHORS:
        to_email = EMAIL_RECIPIENTS.get(author)
        if not to_email:
            results.append({"author": author, "ok": False, "error": "missing recipient"})
            continue
        author_token = generate_token(author)
        link = f"{base_url}/?token={author_token}"
        subject = "Tu token de acceso - Memories"
        body = (
            f"Hola {author},\n\n"
            f"Aquí tienes tu enlace de acceso a Memories:\n{link}\n\n"
            f"Token (por si lo necesitas):\n{author_token}\n\n"
            "Saludos,\nSistema de Memories"
        )
        ok = send_email(subject, body, to_email)
        results.append({"author": author, "ok": ok, "to": to_email, "link": link})

    return {"ok": True, "results": results}


# Goals endpoints
@app.get("/goals", response_model=list[GoalOut])
def list_goals(db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import Goal
    items = db.query(Goal).filter_by(author=author).order_by(Goal.created_at.desc()).all()
    return items


@app.post("/goals", response_model=GoalOut)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import Goal
    now = time.now()
    g = Goal(text=payload.text, author=author, created_at=now)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@app.delete("/goals/{id}")
def delete_goal(id: int, db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import Goal
    g = db.query(Goal).filter_by(id=id, author=author).first()
    if not g:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(g)
    db.commit()
    return {"ok": True}


# Unlinked memories endpoints
@app.get("/unlinked", response_model=list[UnlinkedOut])
def list_unlinked(db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import UnlinkedMemory
    items = db.query(UnlinkedMemory).filter_by(author=author).order_by(UnlinkedMemory.created_at.desc()).all()
    return items


@app.post("/unlinked", response_model=UnlinkedOut)
def create_unlinked(payload: UnlinkedCreate, db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import UnlinkedMemory
    now = time.now()
    u = UnlinkedMemory(text=payload.text, author=author, created_at=now)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@app.delete("/unlinked/{id}")
def delete_unlinked(id: int, db: Session = Depends(get_db), author: str = Depends(get_author)):
    from .models import UnlinkedMemory
    u = db.query(UnlinkedMemory).filter_by(id=id, author=author).first()
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(u)
    db.commit()
    return {"ok": True}
