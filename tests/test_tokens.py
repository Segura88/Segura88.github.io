from datetime import datetime, timezone, timedelta
import pytest

import app.main as main
from app import tokens, models, database
from app.database import SessionLocal, engine


# Setup in-memory DB for tests
models.Base.metadata.create_all(bind=engine)


def test_generate_and_consume_token():
    # generate token
    tok = tokens.generate_email_token('Jaime', ttl_minutes=1)
    assert isinstance(tok, str) and len(tok) > 0

    # consume token
    author = tokens.consume_email_token(tok)
    assert author == 'Jaime'

    # consuming again should return None
    author2 = tokens.consume_email_token(tok)
    assert author2 is None


def test_token_endpoint(client):
    # create a token
    tok = tokens.generate_email_token('Gabi', ttl_minutes=1)

    # call the endpoint
    resp = client.get(f"/token/{tok}")
    assert resp.status_code == 200
    data = resp.json()
    assert data['author'] == 'Gabi'
    assert data['ok'] is True
 