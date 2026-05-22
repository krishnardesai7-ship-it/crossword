#!/usr/bin/env bash
# Render Build Script for Crossword Django App
# This runs before the web server starts on every deploy.

set -o errexit  # exit on error

# Install Python dependencies
pip install -r requirements.txt

# Move into Django source directory
cd src

# Collect static files
python manage.py collectstatic --no-input

# Run all migrations (0020_load_initial_books will auto-load books.json if DB is empty)
python manage.py migrate --no-input

# Load products fixture if products table is empty
python manage.py shell -c "
from myapp.models import product
if not product.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'products.json', verbosity=1)
    print('[build.sh] Products loaded.')
else:
    print('[build.sh] Products already exist, skipping fixture.')
"

# Load books fixture if books table is empty
python manage.py shell -c "
from myapp.models import Book
if not Book.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'books.json', verbosity=1)
    print('[build.sh] Books loaded.')
else:
    print('[build.sh] Books already exist, skipping fixture.')
"

echo "=== Build complete ==="
