#!/bin/sh

set -e

# Setup alembic
./bash_scripts/setup_alembic.sh

# Install main dependencies with poetry
echo "Installing main dependencies..."
poetry install --only main --no-interaction --no-ansi

# Run the Taskipy tasks for generating new migrations and applying them
echo "Running Alembic migrations..."
poetry run task makemigrations
poetry run task migrate

# Start the FastAPI application
echo "Starting FastAPI application..."
poetry run uvicorn kami_pricing_analytics.interface.api.fastapi.app:app --host 0.0.0.0 --port 8001 --reload --log-level debug
