#!/bin/sh

set -e

echo "Starting FastAPI application..."
uvicorn scraper.app:app --host 0.0.0.0 --port 8001 --reload
