#!/usr/bin/env bash
# Make sure we fail on errors
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (SQLite-safe)
python manage.py migrate
