# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authuser', '0002_studentproxymodel_user_batch_user_current_semester_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_flexible_elective_mode',
            field=models.BooleanField(default=False, help_text='Enable flexible elective selection across semesters'),
        ),
    ] 