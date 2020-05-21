from django import forms
from django.utils.translation import ugettext_lazy as _

from utils.generals import get_model

Category = get_model('tryout', 'Category')


class PasswordProtectForm(forms.Form):
    password = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.bundle = kwargs.pop('bundle', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if self.bundle.password != password:
            raise forms.ValidationError(_("Password salah."))
        return password
