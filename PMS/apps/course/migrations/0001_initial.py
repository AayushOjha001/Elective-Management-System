# Generated by Django 5.2.4 on 2025-07-03 13:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Batch',
                'verbose_name_plural': 'Batches',
            },
        ),
        migrations.CreateModel(
            name='ElectiveSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField()),
                ('min_student', models.IntegerField(verbose_name='Minimum student for a subject')),
                ('subjects_provided', models.IntegerField(verbose_name='Subject provided to each student')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.academiclevel')),
            ],
            options={
                'verbose_name': 'Semester',
                'verbose_name_plural': 'Semesters',
            },
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stream_name', models.CharField(max_length=80)),
                ('level', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='course.academiclevel')),
            ],
        ),
        migrations.CreateModel(
            name='ElectiveSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(max_length=80)),
                ('elective_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.electivesession')),
                ('stream', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='course.stream')),
            ],
        ),
    ]
