# Generated by Django 5.2.4 on 2025-07-07 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_alter_electivesubject_min_students'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electivesubject',
            name='max_students',
        ),
        migrations.RemoveField(
            model_name='electivesubject',
            name='min_students',
        ),
    ]
