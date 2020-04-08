from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable, NotFound

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault

Voucher = get_model('market', 'Voucher')
VoucherRedeem = get_model('market', 'VoucherRedeem')


class VoucherRedeemSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    voucher_code = serializers.CharField(read_only=False)

    class Meta:
        model = VoucherRedeem
        fields = ('user', 'voucher_code',)
        extra_kwargs = {
            'user': {'write_only': True},
            'voucher_code': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        user = request.user
        voucher_code = validated_data.pop('voucher_code', None)

        try:
            voucher = Voucher.objects.get(code=voucher_code)
        except ObjectDoesNotExist:
            raise NotFound()

        try:
            obj = VoucherRedeem.objects.create(user=user, voucher=voucher)
            setattr(obj, 'voucher_code', voucher_code)
            return obj
        except ValidationError as e:
            raise NotAcceptable(_(''.join(e.messages)))
