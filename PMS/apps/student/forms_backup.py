import collections

from django import forms

from apps.authuser.models import StudentProxyModel
from apps.student.models import ElectivePriority
from apps.utils import get_student_queryset, get_subjects, get_nth_object, get_object_index


class PriorityForm(forms.ModelForm):
    class Meta:
        model = ElectivePriority
        fields = ('subject', 'priority')


class PriorityFormForFormset(forms.Form):
    student = forms.ModelChoiceField(queryset=StudentProxyModel.objects.all(), required=True)
    desired_number_of_subjects = forms.IntegerField(required=False,  
        label="Desired Number of Subjects",
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.priority_detail_form_data = kwargs.pop('priority_detail_form_data', None)
        super().__init__(*args, **kwargs)
        self.stream = self.priority_detail_form_data.get('stream')
        self.level = self.priority_detail_form_data.get('level')
        self.batch = self.priority_detail_form_data.get('batch')
        self.semester = self.priority_detail_form_data.get('semester')
        self.student_queryset = get_student_queryset(self.batch,
                                                     self.stream)
        self.enter_from_text = self.priority_detail_form_data.get('enter_from_text')
        self.subjects = get_subjects(self.stream, self.semester)

        if self.enter_from_text:
            self.fields['priority_text'] = forms.CharField()
        else:
            for index in range(1, self.subjects.count() + 1):
                field_name = 'priority_%d' % (index)
                self.fields[field_name] = forms.ModelChoiceField(queryset=self.subjects)

        if 'student' in self.initial:
            self.fields['student'].queryset = self.student_queryset.filter(id=self.initial['student'].id)
            priorities_of_student = ElectivePriority.objects.filter(student=self.initial['student'],
                                                                    session=self.semester).order_by('priority')
            if priorities_of_student.exists():
                if self.enter_from_text:
                    self.fields['priority_text'] = forms.CharField(initial=priorities_of_student.first().priority_text)
                else:
                    for index, value in enumerate(priorities_of_student):
                        field_name = 'priority_%d' % (index + 1)
                        self.fields[field_name] = forms.ModelChoiceField(queryset=self.subjects,
                                                                         initial=value.subject.id)

    def clean_priority_text(self):
        try:
            subject_indexing = [int(i) for i in self.cleaned_data.get('priority_text').split(' ')]
        except ValueError:
            raise forms.ValidationError('Please enter numeric data only')
        subject_count = len(subject_indexing)
        if subject_count != self.subjects.count():
            raise forms.ValidationError("Please arrange all the subjects in order")
        repeated_subjects = [item for item, count in collections.Counter(subject_indexing).items() if count > 1]
        if len(repeated_subjects) != 0:
            raise forms.ValidationError('Repeated subjects')
        for i in range(1, subject_count + 1):
            if i not in subject_indexing:
                raise forms.ValidationError('Invalid numbers used')

        return self.cleaned_data.get('priority_text')

    def clean(self, *args, **kwargs):
        super().clean()
        data_copy = self.cleaned_data.copy()
        data_copy.pop('student')        subject_list = []
        for key, value in data_copy.items():
            subject_list.append(value)

        repeated_subjects = [item for item, count in collections.Counter(subject_list).items() if count > 1]
        if len(repeated_subjects) != 0:
            raise forms.ValidationError('Repeated subjects')

    def save(self, *args, **kwargs):
        ElectivePriority.objects.filter(student=self.cleaned_data.get('student'),
                                        session=self.semester).delete()
        student = self.cleaned_data.pop('student', None)
        desired_number_of_subjects = self.cleaned_data.pop('desired_number_of_subjects', None)
        
        if self.enter_from_text:
            priorities = self.cleaned_data.get('priority_text')
            actual_count = len(priorities.split(' '))
            # Use provided desired count or actual count of selections
            final_desired_count = desired_number_of_subjects if desired_number_of_subjects else actual_count
            
            for priority, value in enumerate(priorities.split(' ')):
                index = int(value) - 1
                ElectivePriority.objects.create(student=student, session=self.semester,
                                                subject=get_nth_object(self.subjects, index), priority=priority + 1
                                                , desired_number_of_subjects=final_desired_count)
        else:
            priorities_list = []
            # Count actual number of priority selections
            actual_count = len([key for key in self.cleaned_data.keys() if key.startswith('priority_')])
            # Use provided desired count or actual count of selections
            final_desired_count = desired_number_of_subjects if desired_number_of_subjects else actual_count
            
            for key, value in self.cleaned_data.items():
                priority_int = int(key[9:])  # 9 + 1  letters are 'priority_'
                priorities_list.append(str(get_object_index(self.subjects, value) + 1))                ElectivePriority.objects.create(student=student, session=self.semester,
                                                subject=value, priority=priority_int,
                                                desired_number_of_subjects=final_desired_count)
            priorities = ' '.join(priorities_list)
        ElectivePriority.objects.filter(student=student,
                                        session=self.semester).update(priority_text=priorities)
