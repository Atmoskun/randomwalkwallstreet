#!/usr/bin/env bash

Exit on error

set -o errexit

Install Python dependencies

pip install -r requirements.txt

Collect static files (for Django admin, etc.)

python manage.py collectstatic --noinput

Run database migrations

python manage.py migrate
