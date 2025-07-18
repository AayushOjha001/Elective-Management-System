# Generated by Django 5.2.4 on 2025-07-07 06:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='electivesubject',
            name='max_students',
            field=models.PositiveIntegerField(default=24, verbose_name='Maximum number of students allowed'),
        ),
        migrations.AddField(
            model_name='electivesubject',
            name='min_students',
            field=models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Minimum number of students required'),
        ),
    ]
