from django import forms

from apps.course.models import Stream, ElectiveSession, AcademicLevel, Batch


class StreamForm(forms.Form):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all())
    level = forms.ModelChoiceField(queryset=AcademicLevel.objects.all())
    stream = forms.ModelChoiceField(queryset=Stream.objects.all())
    semester = forms.ModelChoiceField(queryset=ElectiveSession.objects.all())


class PriorityEntryDetailFormset(forms.Form):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all())
    level = forms.ModelChoiceField(queryset=AcademicLevel.objects.all())
    stream = forms.ModelChoiceField(queryset=Stream.objects.all())
    semester = forms.ModelChoiceField(queryset=ElectiveSession.objects.all())
    enter_from_text = forms.BooleanField(initial=False, required=False)
