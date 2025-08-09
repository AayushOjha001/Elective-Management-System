#!/bin/bash

# Exit on any error
set -e

# FORCE correct Django settings
export DJANGO_SETTINGS_MODULE=PMS.settings_production
export DEBUG=0

echo "Starting Elective Management System..."

# Debug environment
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "DEBUG: $DEBUG"
echo "Current directory: $(pwd)"
echo "Data directory exists: $(test -d /app/data && echo 'Yes' || echo 'No')"
echo "Data directory permissions: $(ls -la /app/ | grep data || echo 'Not found')"

# Run Django settings debug script
echo "Running Django settings debug check..."
python debug_settings.py || echo "Debug script failed"

# Ensure data directory exists and has correct permissions
mkdir -p /app/data
chmod 755 /app/data

# Ensure the django user can write to the data directory
if [ "$(id -u)" = "0" ]; then
    # If running as root, change ownership to django user
    chown -R django:django /app/data
else
    # If running as django user, just check permissions
    echo "Running as user: $(whoami)"
    echo "Data directory permissions: $(ls -la /app/data 2>/dev/null || echo 'Directory not accessible')"
fi

# Run migrations
echo "Running database migrations..."
echo "Database path check:"
if [ "$(id -u)" = "0" ]; then
    # Run as django user if we're root
    su django -c 'python -c "
import os
os.environ[\"DJANGO_SETTINGS_MODULE\"] = \"PMS.settings_production\"
import django
django.setup()
from django.conf import settings
print(f\"Database ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}\")
print(f\"Database NAME: {settings.DATABASES[\"default\"][\"NAME\"]}\")
print(f\"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}\")
print(f\"DEBUG: {settings.DEBUG}\")
"'
    su django -c "python manage.py migrate --noinput --settings=PMS.settings_production"
else
    # Run directly if already django user
    python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'PMS.settings_production'
import django
django.setup()
from django.conf import settings
print(f'Database ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'Database NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DEBUG: {settings.DEBUG}')
"
    python manage.py migrate --noinput --settings=PMS.settings_production
fi

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
if [ "$(id -u)" = "0" ]; then
    su django -c 'python manage.py shell --settings=PMS.settings_production << "EOF" || true
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "adminpassword123")
        print("Superuser created successfully")
    else:
        print("Superuser already exists")
except Exception as e:
    print(f"Superuser creation skipped: {e}")
EOF'
else
    python manage.py shell --settings=PMS.settings_production << 'EOF' || true
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
fi

# Collect static files
echo "Collecting static files..."
if [ "$(id -u)" = "0" ]; then
    su django -c "python manage.py collectstatic --noinput --settings=PMS.settings_production"
else
    python manage.py collectstatic --noinput --settings=PMS.settings_production
fi

# Start the application
echo "Starting Gunicorn server..."
echo "Final environment check before starting server:"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "DEBUG: $DEBUG"

if [ "$(id -u)" = "0" ]; then
    # If running as root, switch to django user for the server
    # Ensure environment variables are passed to the django user
    exec su django -c "
        export DJANGO_SETTINGS_MODULE=PMS.settings_production
        export DEBUG=0
        export PYTHONUNBUFFERED=1
        echo 'Starting as django user with DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE'
        exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 PMS.wsgi:application
    "
else
    # If already running as django user, start normally
    export DJANGO_SETTINGS_MODULE=PMS.settings_production
    export DEBUG=0
    echo "Starting as current user with DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
    exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 PMS.wsgi:application
fi
