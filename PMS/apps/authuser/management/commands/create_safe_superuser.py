from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.course.models import Batch, AcademicLevel, Stream, ElectiveSession


class Command(BaseCommand):
    help = 'Create a superuser with all required fields for the custom User model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', 
            default='admin',
            help='Username for the superuser'
        )
        parser.add_argument(
            '--email', 
            default='admin@example.com',
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password', 
            default='adminpassword123',
            help='Password for the superuser'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser already exists!')
            )
            superusers = User.objects.filter(is_superuser=True)
            for user in superusers:
                self.stdout.write(f'   - {user.username}')
            return
        
        try:
            # Ensure required model instances exist
            batch, created = Batch.objects.get_or_create(
                id=1, 
                defaults={'name': 'Default Batch'}
            )
            if created:
                self.stdout.write(f'✅ Created default batch: {batch}')
            
            level, created = AcademicLevel.objects.get_or_create(
                id=1, 
                defaults={'name': 'Default Level'}
            )
            if created:
                self.stdout.write(f'✅ Created default academic level: {level}')
            
            stream, created = Stream.objects.get_or_create(
                id=1, 
                defaults={'stream_name': 'Default Stream', 'level': level}
            )
            if created:
                self.stdout.write(f'✅ Created default stream: {stream}')
            
            # Create or get default ElectiveSession
            session = None
            try:
                session, created = ElectiveSession.objects.get_or_create(
                    id=1,
                    defaults={
                        'level': level,
                        'semester': 1,
                        'min_student': 5,
                        'subjects_provided': 2
                    }
                )
                if created:
                    self.stdout.write(f'✅ Created default elective session: {session}')
            except Exception as e:
                self.stdout.write(f'⚠️ Could not create ElectiveSession: {e}')
                session = None
            
            # Create superuser
            user_data = {
                'username': username,
                'email': email,
                'first_name': 'Admin',
                'last_name': 'User',
                'name': 'Admin User',
                'roll_number': 'ADMIN001',
                'user_type': 'admin',
                'current_semester': session,  # ElectiveSession instance or None
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'batch': batch,
                'level': level,
                'stream': stream,
            }
            
            user = User(**user_data)
            user.set_password(password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Superuser created successfully!')
            )
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Password: {password}')
            self.stdout.write(f'   Email: {user.email}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {e}')
            )
            raise
