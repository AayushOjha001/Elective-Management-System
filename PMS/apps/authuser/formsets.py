from django.contrib.auth import get_user_model
from django.forms.models import BaseInlineFormSet, inlineformset_factory

from apps.authuser.forms import PriorityForm
from apps.authuser.models import StudentProxyModel
from apps.student.models import ElectivePriority

User = get_user_model()


class BasePriorityFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Now we need to make a queryset to each field of each form inline
        # self.queryset = Child.objects.filter(<my custom filter>)

    def _construct_form(self, i, **kwargs):
        kwargs['parent_instance'] = self.instance
        form = super()._construct_form(i, **kwargs)
        form.request = self.request
        return form


PriorityFormSet = inlineformset_factory(StudentProxyModel, ElectivePriority, form=PriorityForm,
                                        formset=BasePriorityFormSet)
