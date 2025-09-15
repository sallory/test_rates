#!/bin/bash
set -e

echo "Building docker images..."
docker-compose -f docker-compose.test.yml up -d --build

echo "Running tests..."
docker-compose -f docker-compose.test.yml run --rm test_rates pytest -vv

echo "Cleaning..."
docker-compose -f docker-compose.test.yml down -v
