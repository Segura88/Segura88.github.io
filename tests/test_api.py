import sys
import os
from datetime import datetime

# ensure project root is on sys.path so `import app` works under pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
import app.main as main
from app.schemas import WeeklyMemoryCreate

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use an in-memory SQLite DB for tests to avoid locking the project's file DB
def setup_test_db():
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(bind=test_engine)

    # Rebind in app.database and in main so code uses the test session
    import app.database as database

    database.engine = test_engine
    database.SessionLocal = TestSessionLocal

    main.engine = test_engine
    main.SessionLocal = TestSessionLocal

    # create tables on the test engine
    main.Base.metadata.create_all(bind=test_engine)

    return TestSessionLocal


TestSessionLocal = setup_test_db()


def test_get_weeks_initial():
    db = TestSessionLocal()
    result = main.get_weeks(db=db)
    assert isinstance(result, list)
    assert any(item["week_monday"].startswith("2026-") for item in result)
    db.close()


def test_post_and_duplicate(monkeypatch):
    db = TestSessionLocal()

    # force time.now() to a Sunday of 2026 (2026-01-04 is a Sunday)
    def fake_now():
        # 2026-01-11 is a Sunday whose week_monday is 2026-01-05 -> allowed
        return datetime(2026, 1, 11, 12, 0, tzinfo=main.time.TZ)

    monkeypatch.setattr(main.time, "now", fake_now)

    payload = WeeklyMemoryCreate(text="Prueba automatizada", author="Test")
    created = main.create_weekly_memory(payload=payload, db=db, author="Jaime")
    assert created.text == payload.text
    assert created.author == "Jaime"

    # duplicate should raise
    try:
        main.create_weekly_memory(payload=payload, db=db, author="Jaime")
        assert False, "Expected duplicate to raise"
    except Exception as e:
        assert "Week already written" in str(e)

    db.close()


def test_post_forbidden(monkeypatch):
    db = TestSessionLocal()

    # force time.now() to a Monday
    def fake_now_monday():
        return datetime(2026, 1, 5, 12, 0, tzinfo=main.time.TZ)

    monkeypatch.setattr(main.time, "now", fake_now_monday)

    payload = WeeklyMemoryCreate(text="No escrito", author="Test")
    try:
        main.create_weekly_memory(payload=payload, db=db, author="Jaime")
        assert False, "Expected forbidden to raise"
    except Exception as e:
        assert "Not writable now" in str(e)

    db.close()
