import sys

from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault
from apps.payment.utils.constant import IN

Bought = get_model('market', 'Bought')
BoughtProofDocument = get_model('market', 'BoughtProofDocument')
AffiliateAcquired = get_model('market', 'AffiliateAcquired')
AffiliateCommission = get_model('market', 'AffiliateCommission')


class BoughtSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Bought
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        user = request.user
        bundle = validated_data.get('bundle', None)
        coin_need = bundle.coin_amount
        coin_amounts = user.account.coin_amounts

        if coin_need > coin_amounts['total_active']:
            raise NotAcceptable(_("Koin tidak cukup silahkan topup."))

        # affiliate
        try:
            affiliate_acquired = AffiliateAcquired.objects.get(user_acquired_id=user.id)
        except ObjectDoesNotExist:
            affiliate_acquired = None

        if affiliate_acquired:
            affiliator = affiliate_acquired.affiliate.user
            amount = coin_need * 0.2
            description = _("Komisi pembelian Bundel %s oleh %s" % (bundle.label, user.username))
            caused_content_type = ContentType.objects \
                .get_for_model(bundle, for_concrete_model=False)
    
            AffiliateCommission.objects.create(
                amount=amount, creator=user, affiliator=affiliator,
                transaction_type=IN, description=description,
                caused_object_id=bundle.id, caused_content_type=caused_content_type)

        obj, _created = Bought.objects.get_or_create(**validated_data)
        return obj


class BoughtProofDocumentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    value_image_url = serializers.SerializerMethodField(read_only=True)
    value_file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BoughtProofDocument
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def validate(self, data):
        if data['value_image']:
            img_size = data['value_image'].size / 1000
            if img_size > 5000:
                raise serializers.ValidationError(_("Max allowed is 5MB each."))

            return data

    def create(self, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()
        
        value_image = validated_data.pop('value_image')

        defaults = {
            'value_image': value_image,
        }
        obj, _created = BoughtProofDocument.objects.update_or_create(**validated_data, defaults=defaults)
        return obj

    def get_value_image_url(self, obj):
        request = self.context['request']

        if obj.value_image:
            return request.build_absolute_uri(obj.value_image.url)
        return None

    def get_value_file_url(self, obj):
        request = self.context['request']

        if obj.value_file:
            return request.build_absolute_uri(obj.value_file.url)
        return None
