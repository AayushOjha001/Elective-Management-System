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

# Set Python path
export PYTHONPATH="/app:$PYTHONPATH"
cd /app

echo "Running migrations..."
python manage.py migrate --noinput --settings=PMS.settings_production_clean

echo "Creating ALL required model instances BEFORE any superuser creation..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF'
try:
    from apps.course.models import Batch, AcademicLevel, Stream, ElectiveSession
    
    print("Creating required model instances in correct order...")
    
    # Create default Batch with id=1 (required by User model default)
    if not Batch.objects.filter(id=1).exists():
        batch = Batch.objects.create(id=1, name='Default Batch')
        print(f"✅ Created default batch: {batch}")
    else:
        batch = Batch.objects.get(id=1)
        print(f"✅ Default batch already exists: {batch}")
    
    # Create default AcademicLevel with id=1 (required by User model default)
    if not AcademicLevel.objects.filter(id=1).exists():
        level = AcademicLevel.objects.create(id=1, name='Default Level')
        print(f"✅ Created default academic level: {level}")
    else:
        level = AcademicLevel.objects.get(id=1)
        print(f"✅ Default academic level already exists: {level}")
    
    # Create default Stream with id=1
    if not Stream.objects.filter(id=1).exists():
        stream = Stream.objects.create(id=1, stream_name='Default Stream', level=level)
        print(f"✅ Created default stream: {stream}")
    else:
        stream = Stream.objects.get(id=1)
        print(f"✅ Default stream already exists: {stream}")
    
    # Create default ElectiveSession (optional, but good to have)
    if not ElectiveSession.objects.filter(id=1).exists():
        session = ElectiveSession.objects.create(
            id=1, 
            level=level, 
            semester=1, 
            min_student=5, 
            subjects_provided=2
        )
        print(f"✅ Created default elective session: {session}")
    else:
        session = ElectiveSession.objects.get(id=1)
        print(f"✅ Default elective session already exists: {session}")
        
    print("✅ All required model instances are ready!")
    
except Exception as e:
    print(f"❌ Error creating required model instances: {e}")
    import traceback
    traceback.print_exc()
    raise  # Stop execution if this fails
EOF

echo "Attempting to create superuser safely..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF'
try:
    from django.contrib.auth import get_user_model
    from apps.course.models import Batch, AcademicLevel, Stream, ElectiveSession
    
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
        
        try:
            # Get the default required foreign key objects
            default_batch = Batch.objects.get(id=1)
            default_level = AcademicLevel.objects.get(id=1)
            default_stream = Stream.objects.get(id=1)
            
            # Get default ElectiveSession (nullable field)
            default_session = None
            try:
                default_session = ElectiveSession.objects.get(id=1)
            except ElectiveSession.DoesNotExist:
                print("No default ElectiveSession found, leaving current_semester as None")
            
            # Create superuser with all required fields
            user_data = {
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'name': 'Admin User',
                'roll_number': 'ADMIN001',
                'user_type': 'admin',
                'current_semester': default_session,  # ElectiveSession instance or None
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'batch': default_batch,
                'level': default_level,
                'stream': default_stream,
            }
            
            user = User(**user_data)
            user.set_password('adminpassword123')
            user.save()
            
            print("✅ Superuser created successfully!")
            print(f"   Username: {user.username}")
            print("   Password: adminpassword123")
            print(f"   Email: {user.email}")
            
        except Exception as create_error:
            print(f"❌ Error creating superuser: {create_error}")
            print("Trying custom management command...")
            
            from django.core.management import call_command
            try:
                call_command('create_safe_superuser', username='admin', email='admin@example.com', password='adminpassword123')
                print("✅ Superuser created via custom management command!")
            except Exception as cmd_error:
                print(f"❌ Custom management command also failed: {cmd_error}")

    # Also create a secondary superuser with different credentials
    try:
        if not User.objects.filter(username='superadmin').exists():
            print("Creating secondary superuser...")
            default_batch = Batch.objects.get(id=1)
            default_level = AcademicLevel.objects.get(id=1)
            default_stream = Stream.objects.get(id=1)
            
            # Get default ElectiveSession (nullable field)
            default_session = None
            try:
                default_session = ElectiveSession.objects.get(id=1)
            except ElectiveSession.DoesNotExist:
                print("No default ElectiveSession found for secondary user, leaving current_semester as None")
            
            user_data = {
                'username': 'superadmin',
                'email': 'superadmin@elective.sys',
                'first_name': 'Super',
                'last_name': 'Admin',
                'name': 'Super Admin',
                'roll_number': 'SUPER001',
                'user_type': 'admin',
                'current_semester': default_session,  # ElectiveSession instance or None
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'batch': default_batch,
                'level': default_level,
                'stream': default_stream,
            }
            
            user = User(**user_data)
            user.set_password('SuperSecure2025!')
            user.save()
            
            print("✅ Secondary superuser created!")
            print(f"   Username: {user.username}")
            print("   Password: SuperSecure2025!")
            print(f"   Email: {user.email}")
        else:
            print("✅ Secondary superuser already exists")
    except Exception as e:
        print(f"❌ Error creating secondary superuser: {e}")

except Exception as e:
    print(f"❌ Error in superuser creation script: {e}")
    import traceback
    traceback.print_exc()
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=PMS.settings_production_clean

echo "Creating required model instances for User model..."
python manage.py shell --settings=PMS.settings_production_clean << 'EOF'
try:
    from apps.course.models import Batch, AcademicLevel, Stream
    
    # Create default Batch if it doesn't exist
    if not Batch.objects.filter(id=1).exists():
        batch = Batch.objects.create(id=1, name='Default Batch')
        print(f"✅ Created default batch: {batch}")
    else:
        print("✅ Default batch already exists")
    
    # Create default AcademicLevel if it doesn't exist
    if not AcademicLevel.objects.filter(id=1).exists():
        level = AcademicLevel.objects.create(id=1, name='Default Level')
        print(f"✅ Created default academic level: {level}")
    else:
        print("✅ Default academic level already exists")
    
    # Create default Stream if it doesn't exist
    if not Stream.objects.filter(id=1).exists():
        level = AcademicLevel.objects.get(id=1)
        stream = Stream.objects.create(id=1, stream_name='Default Stream', level=level)
        print(f"✅ Created default stream: {stream}")
    else:
        print("✅ Default stream already exists")
        
    print("✅ All required model instances are ready")
    
except Exception as e:
    print(f"❌ Error creating required model instances: {e}")
    import traceback
    traceback.print_exc()
EOF

echo "Starting Gunicorn..."
cd /app
export PYTHONPATH="/app:$PYTHONPATH"
exec gunicorn PMS.wsgi_production:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile - \
    --error-logfile -