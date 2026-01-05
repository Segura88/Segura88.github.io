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
from .config import EXTERNAL_BASE_URL



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

    existing = db.query(WeeklyMemory).filter_by(week_monday=monday).first()
    if existing:
        raise HTTPException(status_code=409, detail="Week already written")

    memory = WeeklyMemory(
        week_monday=monday,
        text=payload.text,
        author=author,
        created_at=current,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


# NOTE: development-only token generation endpoint removed for security.

@app.get("/weeks")
def get_weeks(db: Session = Depends(get_db)):
    weeks = time.all_2026_weeks()
    memories = {
        m.week_monday: m
        for m in db.query(WeeklyMemory).all()
    }

    result = []
    for w in weeks:
        if w in memories:
            result.append({
                "week_monday": w.isoformat(),
                "status": "written",
                "author": memories[w].author,
                "text": memories[w].text,
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
