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

echo "Attempting to create superuser safely..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF'
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    print(f"Using User model: {User}")
    print(f"User model fields: {[f.name for f in User._meta.get_fields()]}")
    
    # Check if any superuser exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists")
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"   - {user.username}")
    else:
        print("Creating superuser...")
        
        # Try to create with minimal required fields
        try:
            # Get required fields for the User model
            required_fields = []
            for field in User._meta.get_fields():
                if hasattr(field, 'null') and not field.null and hasattr(field, 'default') and field.default == '':
                    required_fields.append(field.name)
            
            print(f"Required fields: {required_fields}")
            
            # Create user with only essential fields
            user_data = {
                'username': 'admin',
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
            }
            
            # Add any other required fields with default values
            if hasattr(User, 'first_name'):
                user_data['first_name'] = 'Admin'
            if hasattr(User, 'last_name'):
                user_data['last_name'] = 'User'
            
            user = User(**user_data)
            user.set_password('adminpassword123')
            user.save()
            
            print("✅ Superuser created successfully!")
            print(f"   Username: {user.username}")
            print("   Password: adminpassword123")
            
        except Exception as create_error:
            print(f"❌ Error creating superuser: {create_error}")
            print("Trying alternative method...")
            
            # Try using Django's built-in createsuperuser command
            import subprocess
            result = subprocess.run([
                'python', 'manage.py', 'createsuperuser', 
                '--username', 'admin',
                '--email', 'admin@example.com',
                '--noinput'
            ], env={'DJANGO_SUPERUSER_PASSWORD': 'adminpassword123'}, 
            capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Superuser created via createsuperuser command!")
            else:
                print(f"❌ Failed to create superuser: {result.stderr}")

except Exception as e:
    print(f"❌ Error in superuser creation script: {e}")
    import traceback
    traceback.print_exc()
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=PMS.settings_production_clean

echo "Starting Gunicorn..."
exec gunicorn PMS.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile -