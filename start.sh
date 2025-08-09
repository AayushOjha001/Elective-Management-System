#!/bin/bash

# Simple, bulletproof startup script
set -e

echo "=== SIMPLE STARTUP SCRIPT ==="
echo "Forcing production settings..."

# Absolutely force production settings
export DJANGO_SETTINGS_MODULE=PMS.settings_production_clean
export DEBUG=0

echo "Environment:"
echo "  DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "  DEBUG=$DEBUG"

# Ensure data directory exists
mkdir -p /app/data
chmod 755 /app/data

# Change ownership if running as root
if [ "$(id -u)" = "0" ]; then
    chown -R django:django /app/data
fi

echo "Running migrations..."
python manage.py migrate --noinput --settings=PMS.settings_production_clean

echo "Creating superuser..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF' || true
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
    print('Superuser created')
EOF

echo "Creating backup superuser..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

# Create backup admin
if not User.objects.filter(username='superadmin').exists():
    backup_admin = User.objects.create_superuser('superadmin', 'superadmin@example.com', 'super123admin')
    print("✅ Backup superuser created:")
    print("   Username: superadmin")
    print("   Password: super123admin")
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=PMS.settings_production_clean

# Test Django settings
echo "Testing Django configuration..."
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'PMS.settings_production_clean'
import django
django.setup()
from django.conf import settings
print(f'✅ Using settings: {settings.SETTINGS_MODULE}')
print(f'✅ DEBUG: {settings.DEBUG}')
print(f'✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
"

echo "Starting Gunicorn with production WSGI..."
# Use the dedicated production WSGI file
if [ "$(id -u)" = "0" ]; then
    exec su django -c "DJANGO_SETTINGS_MODULE=PMS.settings_production_clean gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 PMS.wsgi_production:application"
else
    exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 PMS.wsgi_production:application
fi
