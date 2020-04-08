from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator

# THIRD PARTY
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAcceptable

from pprint import pprint

# PROJECT UTILS
from utils.generals import get_model
from apps.person.utils.constant import REGISTER_VALIDATION

Profile = get_model('person', 'Profile')
OTPCode = get_model('person', 'OTPCode')


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')

            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# Check duplicate email if has verified
class EmailDuplicateValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        serializer = serializer_field.parent
        data = getattr(serializer, 'initial_data', None)
        username = getattr(data, 'username', None)

        is_exist = User.objects \
            .prefetch_related('account') \
            .select_related('account') \
            .filter(
                email=value,
                account__email_verified=True
            ).exclude(username=username).exists()

        if is_exist:
            raise serializers.ValidationError(_('Email has been used.'))


# Password verification
class PasswordValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        validate_password(value)


class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='person:user-detail', lookup_field='id', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'url',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SingleUserSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True, source='first_name')
    biography = serializers.CharField(read_only=True, source='profile.biography')
    picture = serializers.ImageField(read_only=True, source='profile.picture')

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'biography', 'picture',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6,
                'validators': [PasswordValidator()]
            },
            'username': {
                'min_length': 4,
                'max_length': 15
            },
            'email': {
                'write_only': True,
                'required': True,
                'validators': [EmailValidator(), EmailDuplicateValidator()]
            }
        }

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)

        # check email validate
        try:
            OTPCode.objects.get(identifier=REGISTER_VALIDATION, email=email, is_used=True)
        except ObjectDoesNotExist:
            raise NotAcceptable(_("Email not validated. Register failed!."))

        user = User.objects.create_user(username, email, password)
        user.account.email_verified = True
        user.account.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    biography = serializers.CharField(required=False)
    picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('full_name', 'biography', 'picture',)

    @transaction.atomic
    def update(self, instance, validated_data):
        # to core user
        full_name = validated_data.pop('full_name', None)
        if full_name:
            instance.first_name = full_name
            instance.save()

        # to profile
        biography = validated_data.pop('biography', None)
        if biography:
            instance.profile.biography = biography
            instance.profile.save()

        instance.refresh_from_db()
        return instance
