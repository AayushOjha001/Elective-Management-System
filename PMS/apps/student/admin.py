from django.contrib import admin

# Register your models here.
from apps.student.models import ElectivePriority, CompletedElective, ElectiveSelection


class ElectivePriorityAdmin(admin.ModelAdmin):
    change_list_template = 'admin/priority/priority_change_list.html'
    list_filter = ('session', 'student__batch', 'student__stream')
    search_fields = ('student__roll_number', 'student__name', 'student__stream__stream_name', 'subject__subject_name')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return super().get_queryset(request).filter(student=request.user)


class CompletedElectiveAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester_completed', 'completion_date', 'grade')
    list_filter = ('semester_completed', 'subject__stream', 'student__batch')
    search_fields = ('student__name', 'student__roll_number', 'subject__subject_name')
    date_hierarchy = 'completion_date'


class ElectiveSelectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'target_semester', 'priority', 'is_selected')
    list_filter = ('target_semester', 'subject__stream', 'student__batch', 'is_selected')
    search_fields = ('student__name', 'student__roll_number', 'subject__subject_name')
    list_editable = ('is_selected', 'priority')


admin.site.register(ElectivePriority, ElectivePriorityAdmin)
admin.site.register(CompletedElective, CompletedElectiveAdmin)
admin.site.register(ElectiveSelection, ElectiveSelectionAdmin)
