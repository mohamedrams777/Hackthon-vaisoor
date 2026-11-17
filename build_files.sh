#!/bin/bash

echo "===== BUILD START ====="

# Install dependencies from web/requirements.txt
pip install -r web/requirements.txt

# Move into the Django project directory
cd web

# Collect static files into staticfiles_build/static/
python manage.py collectstatic --noinput --clear

echo "===== BUILD END ====="
