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
    is_flexible_selection = models.BooleanField(default=False, help_text="Allow flexible elective selection across semesters")

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
    
    @property
    def is_masters_student(self):
        """Check if the student is a master's student"""
        if self.student:
            return self.student.level.name.lower() == 'masters'
        return False
    
    def save(self, *args, **kwargs):
        """Override save to set flexible selection based on student level"""
        if self.student:
            # Only allow flexible selection for master's students
            if self.student.level.name.lower() == 'masters':
                self.is_flexible_selection = True
            else:
                self.is_flexible_selection = False
        super().save(*args, **kwargs)


class CompletedElective(models.Model):
    """Model to track completed elective subjects for master's students"""
    student = models.ForeignKey(StudentProxyModel, on_delete=models.CASCADE)
    subject = models.ForeignKey(ElectiveSubject, on_delete=models.CASCADE)
    semester_completed = models.ForeignKey(ElectiveSession, on_delete=models.CASCADE)
    completion_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=5, blank=True, null=True, help_text="Grade received (optional)")
    
    class Meta:
        unique_together = ('student', 'subject')
        verbose_name = 'Completed Elective'
        verbose_name_plural = 'Completed Electives'
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name} ({self.semester_completed})"


class ElectiveSelection(models.Model):
    """Model to track which subjects a student wants to take in a specific semester"""
    student = models.ForeignKey(StudentProxyModel, on_delete=models.CASCADE)
    subject = models.ForeignKey(ElectiveSubject, on_delete=models.CASCADE)
    target_semester = models.ForeignKey(ElectiveSession, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)
    is_selected = models.BooleanField(default=True, help_text="Whether student wants to take this subject")
    
    class Meta:
        unique_together = ('student', 'subject', 'target_semester')
        verbose_name = 'Elective Selection'
        verbose_name_plural = 'Elective Selections'
    
    def __str__(self):
        status = "Selected" if self.is_selected else "Not Selected"
        return f"{self.student.name} - {self.subject.subject_name} ({status})"
    
    @property
    def is_masters_student(self):
        """Check if the student is a master's student"""
        if self.student:
            return self.student.level.name.lower() == 'masters'
        return False
    
    def save(self, *args, **kwargs):
        """Override save to set is_selected based on student level"""
        if self.student:
            # Bachelor's students must always have is_selected=True (no choice)
            if self.student.level.name.lower() != 'masters':
                self.is_selected = True
        super().save(*args, **kwargs)
