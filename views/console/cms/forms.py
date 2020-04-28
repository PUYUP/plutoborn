from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from utils.generals import get_model

CMSVideo = get_model('cms', 'CMSVideo')
CMSBanner = get_model('cms', 'CMSBanner')


class CMSVideoForm(forms.ModelForm):
    class Meta:
        model = CMSVideo
        fields = '__all__'


class CMSBannerForm(forms.ModelForm):
    class Meta:
        model = CMSBanner
        fields = '__all__'
