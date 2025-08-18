#!/usr/bin/env python
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append('/home/aayush/Desktop/Elective-Management-System/PMS')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

from apps.course.models import AcademicLevel

print('Current AcademicLevel records:')
existing_levels = AcademicLevel.objects.all()
for level in existing_levels:
    print(f'- {level.name} (ID: {level.id})')

print(f'Total count: {existing_levels.count()}')

# Ensure the required academic levels exist
required_levels = ['Bachelor', 'Masters']

for level_name in required_levels:
    level, created = AcademicLevel.objects.get_or_create(name=level_name)
    if created:
        print(f'✅ Created: {level.name} (ID: {level.id})')
    else:
        print(f'ℹ️  Already exists: {level.name} (ID: {level.id})')

print('\nFinal AcademicLevel records:')
for level in AcademicLevel.objects.all():
    print(f'- {level.name} (ID: {level.id})')
