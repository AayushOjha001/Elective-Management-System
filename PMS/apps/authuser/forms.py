import io
import random
import string

from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.course.models import Stream, Batch, AcademicLevel, ElectiveSubject, ElectiveSession
from apps.student.models import StudentProxyModel, ElectivePriority
from apps.system.email_sending_utils import send_account_creation_email

User = get_user_model()
NAME_FIELD = 'Name'
ROLL_NUMBER_FIELD = 'Roll number'
EMAIL_FIELD = 'Email'
REQUIRED_FIELDS = [NAME_FIELD, ROLL_NUMBER_FIELD, EMAIL_FIELD]


def pw_gen(size=8, chars=string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.choice(chars) for _ in range(size))


class NewStudentCreateForm(UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    roll_number = forms.CharField(required=True)
    stream = forms.ModelChoiceField(queryset=Stream.objects.all())

    def is_valid(self):
        if not self.data._mutable:
            self.data._mutable = True
        password = pw_gen()
        self.data['password1'] = password
        self.data['password2'] = password
        is_valid = super().is_valid()
        if is_valid:
            send_account_creation_email(self.data, password)
        return is_valid

    class Meta:
        model = StudentProxyModel
        fields = ('first_name', 'last_name', 'username', 'roll_number', 'stream')


class StudentChangeForm(UserChangeForm):
    class Meta:
        model = StudentProxyModel
        fields = ()


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise forms.ValidationError("Only CSV file is accepted")
    import csv
    decoded_file = value.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.reader(io_string, delimiter=',', quotechar='|')
    row = next(reader)
    for field in REQUIRED_FIELDS:
        if field not in row:
            raise forms.ValidationError(
                " \'%s\' field is not present in the uploaded file. Required fields are %s " % (
                    field, ', '.join(REQUIRED_FIELDS)))
    value.seek(0)


class DetailsForUploadingCSVForm(forms.Form):
    academic_level = forms.ModelChoiceField(queryset=AcademicLevel.objects.all())
    batch = forms.ModelChoiceField(queryset=Batch.objects.all())
    faculty = forms.ModelChoiceField(queryset=Stream.objects.all())
    csv_file = forms.FileField(validators=[validate_file_extension], )


class PriorityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.parent_instance = kwargs.pop('parent_instance', None)
        super().__init__(*args, **kwargs)
        if self.parent_instance is not None:
            current_session = self.parent_instance.current_semester
            stream = self.parent_instance.stream
            subjects = ElectiveSubject.objects.filter(elective_for=current_session, stream=stream)
            self.fields['subject'].queryset = subjects

    class Meta:
        model = ElectivePriority
        exclude = ()


class StudentActionForm(ActionForm):
    semester = forms.ModelChoiceField(ElectiveSession.objects.all(), required=False)
