#!/usr/bin/env python
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append('/home/aayush/Desktop/Elective-Management-System/PMS')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

try:
    from apps.course.models import AcademicLevel
    from apps.course.forms import PriorityEntryDetailFormset
    print("✅ Successfully imported required modules")
except Exception as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

print("=== Testing AcademicLevel records ===")
levels = AcademicLevel.objects.all()
print(f"Found {levels.count()} AcademicLevel records:")
for level in levels:
    print(f"  - {level.name} (ID: {level.id})")

print("\n=== Testing PriorityEntryDetailFormset ===")
form = PriorityEntryDetailFormset()
print("Form instantiated successfully!")

print("\n=== Testing level field queryset ===")
level_field = form.fields['level']
level_queryset = level_field.queryset
print(f"Level field queryset count: {level_queryset.count()}")
for level in level_queryset:
    print(f"  - {level.name} (ID: {level.id})")

print("\n=== Checking form rendering ===")
level_field_html = str(level_field)
print("Level field HTML (first 200 chars):")
print(level_field_html[:200] + "..." if len(level_field_html) > 200 else level_field_html)

# Check if the options are populated
if "Bachelor" in level_field_html and "Masters" in level_field_html:
    print("\n✅ SUCCESS: Both Bachelor and Masters options are available in the form!")
elif level_queryset.count() > 0:
    print(f"\n⚠️  WARNING: Form has {level_queryset.count()} level options but Bachelor/Masters might not be named correctly")
else:
    print("\n❌ ERROR: No level options found in the form")

# If we have records but they don't exist, create them
if levels.count() == 0:
    print("\n=== Creating required AcademicLevel records ===")
    bachelor = AcademicLevel.objects.create(name='Bachelor')
    masters = AcademicLevel.objects.create(name='Masters')
    print(f"Created: {bachelor.name} (ID: {bachelor.id})")
    print(f"Created: {masters.name} (ID: {masters.id})")
    
    # Test form again
    print("\n=== Re-testing form after creating records ===")
    form = PriorityEntryDetailFormset()
    level_field = form.fields['level']
    level_queryset = level_field.queryset
    print(f"Level field queryset count: {level_queryset.count()}")
    for level in level_queryset:
        print(f"  - {level.name} (ID: {level.id})")
