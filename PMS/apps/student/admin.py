from django.contrib import admin

# Register your models here.
from apps.student.models import ElectivePriority


class ElectivePriorityAdmin(admin.ModelAdmin):
    change_list_template = 'admin/priority/priority_change_list.html'
    list_filter = ('session', 'student__batch', 'student__stream')
    search_fields = ('student__roll_number', 'student__name', 'student__stream__stream_name', 'subject__subject_name')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        else:
            return super().get_queryset(request).filter(student=request.user)


# admin.site.register(ElectivePriority, ElectivePriorityAdmin)
