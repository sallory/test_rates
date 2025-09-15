#!/bin/sh
set -e

echo "Starting application..."

exec uvicorn rates.main:app --host 0.0.0.0 --port 8080 --reload
