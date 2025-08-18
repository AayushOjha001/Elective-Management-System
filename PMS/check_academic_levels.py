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

print('AcademicLevel records:')
for level in AcademicLevel.objects.all():
    print(f'- {level.name} (ID: {level.id})')
print(f'Total count: {AcademicLevel.objects.count()}')

# If no records exist, let's create some sample data
if AcademicLevel.objects.count() == 0:
    print("\nNo AcademicLevel records found. Creating sample data...")
    bachelor = AcademicLevel.objects.create(name='Bachelor')
    masters = AcademicLevel.objects.create(name='Masters')
    print(f'Created: {bachelor.name} (ID: {bachelor.id})')
    print(f'Created: {masters.name} (ID: {masters.id})')
