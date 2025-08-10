# Generated data migration for default model instances

from django.db import migrations


def create_default_data(apps, schema_editor):
    """Create default data required by the User model foreign keys"""
    
    # Get model classes
    Batch = apps.get_model('course', 'Batch')
    AcademicLevel = apps.get_model('course', 'AcademicLevel')
    Stream = apps.get_model('course', 'Stream')
    ElectiveSession = apps.get_model('course', 'ElectiveSession')
    
    # Create default Batch with id=1 (required by User model default)
    if not Batch.objects.filter(id=1).exists():
        batch = Batch.objects.create(id=1, name='Default Batch')
        print(f"✅ Migration created default batch: {batch}")
    
    # Create default AcademicLevel with id=1 (required by User model default)
    if not AcademicLevel.objects.filter(id=1).exists():
        level = AcademicLevel.objects.create(id=1, name='Default Level')
        print(f"✅ Migration created default academic level: {level}")
    else:
        level = AcademicLevel.objects.get(id=1)
    
    # Create default Stream with id=1
    if not Stream.objects.filter(id=1).exists():
        stream = Stream.objects.create(id=1, stream_name='Default Stream', level=level)
        print(f"✅ Migration created default stream: {stream}")
    
    # Create default ElectiveSession (optional)
    if not ElectiveSession.objects.filter(id=1).exists():
        session = ElectiveSession.objects.create(
            id=1, 
            level=level, 
            semester=1, 
            min_student=5, 
            subjects_provided=2
        )
        print(f"✅ Migration created default elective session: {session}")


def reverse_default_data(apps, schema_editor):
    """Remove default data (for migration rollback)"""
    
    # Get model classes
    Batch = apps.get_model('course', 'Batch')
    AcademicLevel = apps.get_model('course', 'AcademicLevel')
    Stream = apps.get_model('course', 'Stream')
    ElectiveSession = apps.get_model('course', 'ElectiveSession')
    
    # Remove default instances (be careful with cascading deletes)
    ElectiveSession.objects.filter(id=1).delete()
    Stream.objects.filter(id=1).delete()
    AcademicLevel.objects.filter(id=1).delete()
    Batch.objects.filter(id=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_electivesubject_max_students_and_more'),
    ]

    operations = [
        migrations.RunPython(
            code=create_default_data,
            reverse_code=reverse_default_data,
        ),
    ]
