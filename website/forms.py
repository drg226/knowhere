from website.models import NotificationZone, Group, Notification
from django.forms import ModelForm, CharField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from haystack.forms import SearchForm


class NotificationZoneForm(ModelForm):
    helper = FormHelper()
    helper.form_tag
    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = NotificationZone
        exclude = ['user', 'latitude', 'longitude']


class GroupForm(ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Group
        exclude = ['admin', 'users']


class GroupRemovalForm(ModelForm):
    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = 'group_delete'
    helper.add_input(Submit('submit', 'Remove'))

    class Meta:
        model = Group
        exclude = ['users']


class NotificationForm(ModelForm):
    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Notification
        exclude = ['user', 'latitude', 'longitude']


class GroupSearchForm(SearchForm):
    helper = FormHelper()
    helper._form_method = 'get'
    helper.add_input(Submit('search', 'Search'))

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(GroupSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        return sqs