from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from utils.generals import get_model

Bundle = get_model('market', 'Bundle')


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        exclude = ('packet', 'password',)
        extra_kwargs = {
            'user': {'write_only': True}
        }
