import time

import psycopg2
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def postgres_dsn() -> str:
  return f"host={settings.POSTGRES_HOST} port={settings.POSTGRES_PORT} user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD} dbname={settings.POSTGRES_DB}"


def wait_for_postgres():
  last_error = None
  for _ in range(30):
    try:
      conn = psycopg2.connect(postgres_dsn())
      conn.close()
      return
    except Exception as exc:
      last_error = exc
      time.sleep(1)
  raise RuntimeError(f"PostgreSQL is not available: {last_error}")


def truncate():
  conn = psycopg2.connect(postgres_dsn())
  conn.autocommit = True
  cur = conn.cursor()
  cur.execute("TRUNCATE TABLE call, meeting, manager, company RESTART IDENTITY CASCADE")
  cur.close()
  conn.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
  wait_for_postgres()
  command.upgrade(Config("app/alembic.ini"), "head")
  yield


@pytest.fixture(autouse=True)
def clean_tables(setup_db):
  truncate()
  yield


@pytest.fixture(scope="session")
def client(setup_db):
  with TestClient(app) as test_client:
    yield test_client
