from django.db import models


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

    def __str__(self):
        return self.subject_name
