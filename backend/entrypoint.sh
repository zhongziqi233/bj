#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  python - <<'PY'
import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

database_url = os.environ.get("DATABASE_URL")

for attempt in range(1, 61):
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database is ready.")
        break
    except SQLAlchemyError as exc:
        print(f"Waiting for database ({attempt}/60): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time.")
PY
fi

flask --app wsgi:app init-db
exec "$@"

