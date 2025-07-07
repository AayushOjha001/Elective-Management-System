from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
# Create your models here.


class Batch(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'


class AcademicLevel(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class ElectiveSession(models.Model):
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE)
    semester = models.IntegerField()
    min_student = models.IntegerField(verbose_name='Minimum student for a subject')
    subjects_provided = models.IntegerField(verbose_name='Subject provided to each student', )

    def __str__(self):
        return '%sth semester  of %s' % (self.semester, self.level)

    class Meta:
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'


class Stream(models.Model):
    stream_name = models.CharField(max_length=80)
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.stream_name


class ElectiveSubject(models.Model):
    subject_name = models.CharField(max_length=80)
    elective_for = models.ForeignKey(ElectiveSession, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.PROTECT)
    min_students = models.PositiveIntegerField(
        verbose_name='Minimum number of students required',
        default=10,
        validators=[MinValueValidator(5)]
    )
    max_students = models.PositiveIntegerField(
        verbose_name='Maximum number of students allowed',
        default=24
    )

    def clean(self):
        if self.max_students <= self.min_students:
            raise ValidationError(
                {'max_students': 'Maximum students must be greater than minimum students.'}
            )

    def __str__(self):
        return self.subject_name
