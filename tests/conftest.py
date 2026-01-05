import sys
import os
import pytest
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app.main as main

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def setup_test_db():
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(bind=test_engine)

    import app.database as database

    database.engine = test_engine
    database.SessionLocal = TestSessionLocal

    main.engine = test_engine
    main.SessionLocal = TestSessionLocal

    main.Base.metadata.create_all(bind=test_engine)

    return TestSessionLocal


TestSessionLocal = setup_test_db()


@pytest.fixture
def client():
    client = TestClient(main.app)
    yield client
