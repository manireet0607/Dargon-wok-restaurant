#!/bin/sh
# Container start-up: wait for the database, run migrations, optionally seed, start the API.
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  i=0
  until alembic upgrade head; do
    i=$((i+1))
    if [ "$i" -ge 30 ]; then echo "Database is not reachable. Giving up."; exit 1; fi
    echo "Database not ready yet (attempt $i/30). Retrying in 3 seconds..."
    sleep 3
  done
fi

if [ "${RUN_SEED:-false}" = "true" ]; then
  python -m app.db.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${WEB_CONCURRENCY:-2}" --proxy-headers
