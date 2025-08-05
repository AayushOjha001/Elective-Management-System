from django.contrib import admin
# Register your models here.
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from apps.authuser.models import StudentProxyModel
from apps.course.forms import StreamForm
from apps.course.models import ElectiveSubject, Stream, Batch, ElectiveSession, AcademicLevel
from apps.utils import normalize_result


class StreamAdmin(admin.ModelAdmin):
    list_display = ('stream_name', 'level')
    list_filter = ('level',)


class ElectiveSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'elective_for', 'stream')
    list_filter = ('elective_for', 'stream')
    
    class Media:
        js = ('admin/js/elective_subject_form.js',)


class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch_actions')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate_report/<int:batch_id>',
                self.admin_site.admin_view(self.display_report),
                name='generate_report',
            ),
        ]
        return urls + custom_urls

    def batch_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">View Result</a>&nbsp;',
            reverse('admin:generate_report', args=[obj.id]),
        )

    def display_report(self, request, batch_id, *args, **kwargs):
        batch = self.get_object(request=request, object_id=batch_id)
        context = self.admin_site.each_context(request)
        if request.method == 'GET':
            form = StreamForm()
        else:
            form = StreamForm(request.POST)
            if form.is_valid():
                stream = form.cleaned_data.get('stream', None)
                semester = form.cleaned_data.get('semester', None)
                level = form.cleaned_data.get('level', None)
                subjects = ElectiveSubject.objects.filter(elective_for=semester, stream=stream).values_list('id',
                                                                                                            flat=True)
                student_queryset = StudentProxyModel.objects.filter(batch=batch, stream=stream)

                # Legacy algorithm usage - commented out since using GenericAlgorithm now
                # AlgorithClass = get_suitable_algorithm_class(semester.subjects_provided)
                # algorithm = AlgorithClass(student_queryset, semester, list(subjects))
                # algorithm.run()
                # print(algorithm.get_result())
                # context['result'] = normalize_result(algorithm.get_result())
                # print(normalize_result(algorithm.get_result()))
                # context['is_download'] = '_get_pdf' in request.POST
        context['form'] = form
        # if '_get_pdf' in request.POST:
        #     return Render.render('admin/course/display_report.html', context)
        return TemplateResponse(
            request,
            'admin/course/display_report.html',
            context
        )


class LevelAdmin(admin.ModelAdmin):
    pass


class ElectiveSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(ElectiveSubject, ElectiveSubjectAdmin)
admin.site.register(Stream, StreamAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(AcademicLevel, LevelAdmin)
admin.site.register(ElectiveSession, ElectiveSessionAdmin)
