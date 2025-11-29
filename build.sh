#!/usr/bin/env bash
set -o errexit


# Run DB migrations
flask db upgrade

# Start Gunicorn
exec gunicorn --config gunicorn-cfg.py app:app
