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


class ElectiveRequirement(models.Model):
    """Model to track elective requirements for master's students"""
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE)
    total_electives_required = models.IntegerField(default=6, help_text="Total number of elective subjects required to graduate")
    min_electives_per_semester = models.IntegerField(default=1, help_text="Minimum elective subjects to take per semester")
    max_electives_per_semester = models.IntegerField(default=3, help_text="Maximum elective subjects to take per semester")
    
    class Meta:
        unique_together = ('stream', 'level')
        verbose_name = 'Elective Requirement'
        verbose_name_plural = 'Elective Requirements'
    
    def __str__(self):
        return f"{self.stream} - {self.level} (Required: {self.total_electives_required})"


class StudentElectiveProgress(models.Model):
    """Model to track individual student's elective progress"""
    student = models.OneToOneField('authuser.StudentProxyModel', on_delete=models.CASCADE)
    requirement = models.ForeignKey(ElectiveRequirement, on_delete=models.CASCADE)
    completed_electives = models.IntegerField(default=0, help_text="Number of elective subjects completed")
    target_completion_semester = models.ForeignKey(ElectiveSession, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Student Elective Progress'
        verbose_name_plural = 'Student Elective Progress'
    
    def __str__(self):
        return f"{self.student.name} - {self.completed_electives}/{self.requirement.total_electives_required}"
    
    @property
    def remaining_electives(self):
        return self.requirement.total_electives_required - self.completed_electives
    
    @property
    def completion_percentage(self):
        if self.requirement.total_electives_required > 0:
            return (self.completed_electives / self.requirement.total_electives_required) * 100
        return 0
