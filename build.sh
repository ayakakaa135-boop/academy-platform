#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Update translation fields
python manage.py update_translation_fields --no-input || echo "Translation fields update skipped"

# Create cache table (if using database cache)
python manage.py createcachetable || echo "Cache table creation skipped"

echo "Build completed successfully!"
