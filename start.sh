#!/bin/bash

# Exit on any error
set -e

echo "Starting Elective Management System..."

# Run migrations
echo "Running database migrations..."
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
