from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.student.models import StudentProxyModel, ElectivePriority

User = get_user_model()

STUDENT_GROUP_NAME = 'STUDENT'


@receiver(post_save, sender=StudentProxyModel)
def create_student_account(sender, instance, created, *args, **kwargs):
    if created:
        instance.user_type = 'Student'
        instance.is_staff = True
        instance.save()
        student_group, created = Group.objects.get_or_create(name=STUDENT_GROUP_NAME)
        instance.groups.add(student_group)


@receiver(pre_save, sender=ElectivePriority)
def manage_priority_sememter(sender, instance, *args, **kwargs):
    if instance.student.current_semester is not  None:
        instance.session = instance.student.current_semester
