from django.forms import formset_factory, BaseFormSet

from apps.student.forms import PriorityFormForFormset

BasePriorityFormset = formset_factory(PriorityFormForFormset, formset=BaseFormSet, max_num=50)


class PriorityFormset(BasePriorityFormset):
    extra = 0

    def __init__(self, *args, **kwargs):
        self.priority_detail_form_data = kwargs.pop('priority_detail_form_data', None)
        super(PriorityFormset, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        for form in self.forms:
            if form.is_valid():
                form.save()

    def _construct_form(self, *args, **kwargs):
        # inject user in each form on the formset
        kwargs['priority_detail_form_data'] = self.priority_detail_form_data
        return super()._construct_form(*args, **kwargs)
