#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z db 5432; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
