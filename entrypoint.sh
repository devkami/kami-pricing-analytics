#!/bin/sh

set -e

echo "Starting FastAPI application..."
uvicorn kami_pricing_analytics.interface.api.fastapi.app:app --host 0.0.0.0 --port 8001 --reload
