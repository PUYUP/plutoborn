from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

# THIRD PARTY
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault

Attachment = get_model('tryout', 'Attachment')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        exclude = ('id', 'object_id', 'content_type',)


class CreateAttachmentSerializer(serializers.ModelSerializer):
    uploader = serializers.HiddenField(default=CurrentUserDefault())
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Attachment
        exclude = ('date_created', 'date_updated',)
        extra_kwargs = {
            'uploader': {'write_only': True}
        }

    def __init__(self, **kwargs):
        data = kwargs['data']
        print(kwargs)

        try:
            upload = data['upload']
        except KeyError:
            upload = None

        if upload:
            kwargs['data']['value_image'] = upload
        super().__init__(**kwargs)

    def get_url(self, obj):
        request = self.context['request']

        if obj.value_image:
            return request.build_absolute_uri(obj.value_image.url)
        return None

    @transaction.atomic
    def create(self, validated_data):
        return Attachment.objects.create(**validated_data)
