from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from apps.authuser.models import StudentProxyModel
from apps.course.models import ElectiveSubject, ElectiveSession

User = get_user_model()


class ElectivePriority(models.Model):
    subject = models.ForeignKey(ElectiveSubject, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1, blank=True)
    student = models.ForeignKey(StudentProxyModel, on_delete=models.CASCADE, blank=True, null=True)
    session = models.ForeignKey(ElectiveSession, verbose_name='Semester', on_delete=models.DO_NOTHING)
    priority_text = models.CharField(max_length=100, blank=True, null=True)

    desired_number_of_subjects = models.IntegerField(default=2)

    class Meta:
        unique_together = ('subject', 'session', 'priority', 'student')
        verbose_name = 'Priority'
        verbose_name_plural = 'Priorities'

    def __str__(self):
        try:
            return '%s has priority %d' % (self.subject.subject_name
                                           , self.priority)
        except:
            return ''
