import csv
import io

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from apps.authuser.forms import NewStudentCreateForm, StudentChangeForm, DetailsForUploadingCSVForm, NAME_FIELD, \
    ROLL_NUMBER_FIELD, EMAIL_FIELD, PriorityForm, StudentActionForm
from apps.authuser.formsets import PriorityFormSet
from apps.authuser.models import StudentProxyModel, User
from apps.course.models import ElectiveSubject
from apps.student.models import ElectivePriority

User = get_user_model()


class PriorityInline(admin.TabularInline):
    model = ElectivePriority
    extra = 5
    fields = ('subject', 'priority')
    form = PriorityForm
    formset = PriorityFormSet

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        current_session = obj.current_semester
        stream = obj.stream
        subjects_count = ElectiveSubject.objects.filter(elective_for=current_session, stream=stream).count()
        return subjects_count

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset


class StudentAdmin(UserAdmin):
    add_form = NewStudentCreateForm
    form = StudentChangeForm
    inlines = (PriorityInline,)
    actions = ['change_semester', ]
    action_form = StudentActionForm
    search_fields = ('name', 'username', 'email', 'roll_number')
    list_display = ('name', 'roll_number', 'email', 'batch', 'stream', 'level')
    list_filter = ('batch', 'level', 'stream')
    change_list_template = 'admin/authuser/authuser_student_change_list.html'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email', 'batch', 'stream', 'roll_number', 'current_semester')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'roll_number', 'username', 'email', 'batch', 'stream', 'current_semester'),
        }),
    )
    prepopulated_fields = {'username': ('roll_number',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return super().get_queryset(request)
        return queryset.filter(id=request.user.id)

    def change_semester(self, request, queryset):
        if queryset.exists():
            semester = request.POST.get('semester', None)
            if semester is not None:
                queryset.update(current_semester=semester)
                messages.success(request, 'Updated %d students record' % queryset.count())

            else:
                messages.error(request, 'No semester selected.')
        else:
            messages.error(request, 'No note selected.')

    change_semester.short_description = "Change Semester"

    def get_urls(self, *args, **kwargs):
        urls = super().get_urls(*args, **kwargs)
        custom_urls = [
            path('upload-student-csv', self.admin_site.admin_view(self.handle_csv_upload), name='handle-csv-upload')
            # path('enter-priority', self.admin_site.admin_view(self.handle_csv_upload), name='handle-csv-upload')
        ]
        return custom_urls + urls

    @staticmethod
    def create_student_record_from_uploaded_csv(csv_file, academic_level, batch, faculty):
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string, delimiter=',', quotechar='|')
        list_of_created_username = []
        for row in reader:
            name = row.get(NAME_FIELD)
            roll_number = row.get(ROLL_NUMBER_FIELD)
            email = row.get(EMAIL_FIELD)

            try:
                user = User.objects.create(username=roll_number, name=name, roll_number=roll_number,
                                           level=academic_level, email=email,
                                           batch=batch, stream=faculty, user_type='Student')
                list_of_created_username.append(roll_number)
            except IntegrityError as e:
                for username in list_of_created_username:
                    User.objects.get(username=username).delete()
                raise IntegrityError(
                    'A student with roll number %s is already registered. Please handle this manually.' % (
                        roll_number,))

    # def handle_priority_upload(self, request, *args, **kwargs):
    #     student_object = self.get_object(request)
    #     context = self.admin_site.each_context(request)

    def handle_csv_upload(self, request, *args, **kwargs):
        context = self.admin_site.each_context(request)
        if request.method != 'POST':
            form = DetailsForUploadingCSVForm
        else:
            form = DetailsForUploadingCSVForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    academic_level = form.cleaned_data.get('academic_level')
                    batch = form.cleaned_data.get('batch')
                    faculty = form.cleaned_data.get('faculty')
                    csv_file = request.FILES['csv_file']
                    self.create_student_record_from_uploaded_csv(csv_file, academic_level, batch, faculty)
                    return redirect(reverse('admin:authuser_studentproxymodel_changelist'))
                except Exception as e:
                    self.message_user(request, 'Failure: ' + str(e), messages.ERROR)

        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = 'Upload csv with students detail'
        return TemplateResponse(
            request,
            'admin/authuser/upload_csv.html',
            context,
        )


admin.site.register(StudentProxyModel, StudentAdmin)
admin.site.unregister(Group)

admin.site.site_header = 'Elective Priority Management System'
admin.site.site_title = 'EPMS Admin'
admin.site.site_url = 'https://epms.abhinavdev.com.np/'
admin.site.index_title = 'Elective Priority Management System'
admin.empty_value_display = '----'
