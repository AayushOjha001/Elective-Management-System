#!/bin/bash

# Exit on any error
set -e

echo "Starting Elective Management System..."

# Debug environment
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"
echo "Current directory: $(pwd)"
echo "Data directory exists: $(test -d /app/data && echo 'Yes' || echo 'No')"
echo "Data directory permissions: $(ls -la /app/ | grep data || echo 'Not found')"

# Ensure data directory exists and has correct permissions
mkdir -p /app/data
chmod 755 /app/data

# Run migrations
echo "Running database migrations..."
echo "Database path check:"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings_production')
import django
django.setup()
from django.conf import settings
print(f'Database ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Database NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DEBUG: {settings.DEBUG}')
"
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << 'EOF' || true
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
        print('Superuser created successfully')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Superuser creation skipped: {e}')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 PMS.wsgi:application
