from django.contrib import admin

# Register your models here.
from apps.student.models import ElectivePriority, CompletedElective, ElectiveSelection


class ElectivePriorityAdmin(admin.ModelAdmin):
    change_list_template = 'admin/priority/priority_change_list.html'
    list_filter = ('session', 'student__batch', 'student__stream', 'student__level')
    search_fields = ('student__roll_number', 'student__name', 'student__stream__stream_name', 'subject__subject_name')
    list_display = ('student', 'subject', 'session', 'priority', 'is_flexible_selection', 'student_level')
    readonly_fields = ('is_flexible_selection',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return super().get_queryset(request).filter(student=request.user)
    
    def student_level(self, obj):
        """Display student's academic level"""
        if obj.student:
            return obj.student.level.name
        return "N/A"
    student_level.short_description = "Student Level"
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on student level"""
        if obj and obj.student and obj.student.level.name.lower() == 'masters':
            # Show flexible selection options for master's students
            return (
                (None, {
                    'fields': ('student', 'subject', 'session', 'priority', 'desired_number_of_subjects', 'is_flexible_selection')
                }),
            )
        else:
            # Hide flexible selection for bachelor's students
            return (
                (None, {
                    'fields': ('student', 'subject', 'session', 'priority', 'desired_number_of_subjects')
                }),
            )


class CompletedElectiveAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester_completed', 'completion_date', 'grade')
    list_filter = ('semester_completed', 'subject__stream', 'student__batch')
    search_fields = ('student__name', 'student__roll_number', 'subject__subject_name')
    date_hierarchy = 'completion_date'


class ElectiveSelectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'target_semester', 'priority', 'is_selected', 'student_level')
    list_filter = ('target_semester', 'subject__stream', 'student__batch', 'student__level', 'is_selected')
    search_fields = ('student__name', 'student__roll_number', 'subject__subject_name')
    list_editable = ('priority',)  # Only allow editing priority, not is_selected
    
    def student_level(self, obj):
        """Display student's academic level"""
        if obj.student:
            return obj.student.level.name
        return "N/A"
    student_level.short_description = "Student Level"
    
    def get_list_editable(self, request):
        """Only allow editing is_selected for master's students"""
        if request.user.is_superuser:
            # For superusers, check if any selected items are master's students
            if request.GET.get('student__level__name__exact', '').lower() == 'masters':
                return ('is_selected', 'priority')
            return ('priority',)
        return ('priority',)
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets based on student level"""
        if obj and obj.student and obj.student.level.name.lower() == 'masters':
            # Show is_selected option for master's students
            return (
                (None, {
                    'fields': ('student', 'subject', 'target_semester', 'priority', 'is_selected')
                }),
            )
        else:
            # Hide is_selected for bachelor's students (always True)
            return (
                (None, {
                    'fields': ('student', 'subject', 'target_semester', 'priority')
                }),
            )


admin.site.register(ElectivePriority, ElectivePriorityAdmin)
admin.site.register(CompletedElective, CompletedElectiveAdmin)
admin.site.register(ElectiveSelection, ElectiveSelectionAdmin)
