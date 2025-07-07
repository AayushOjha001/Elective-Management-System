from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# Create your models here.
from apps.course.models import Stream, Batch, AcademicLevel, ElectiveSession

USER_TYPE_CHOICES = (
    ('Student', 'Student'),
    ('Staff', 'Staff')
)


class StudentObjectsManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type='Student')


class User(AbstractUser):
    name = models.CharField(max_length=80, default='')
    stream = models.ForeignKey(Stream, null=True, blank=True, on_delete=models.PROTECT)
    roll_number = models.CharField(max_length=30, default='123')
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=30, default='Staff')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, default=1)
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE, default=1)
    current_semester = models.ForeignKey(ElectiveSession, on_delete=models.DO_NOTHING, null=True)
    is_flexible_elective_mode = models.BooleanField(default=False, help_text="Enable flexible elective selection across semesters")

    def get_full_name(self):
        return self.name


class StudentProxyModel(User):
    objects = StudentObjectsManager()

    def __str__(self):
        return '%s (%s)' % (self.get_full_name(), self.username)

    class Meta:
        proxy = True
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
