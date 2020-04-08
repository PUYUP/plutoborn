from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault
from apps.payment.utils.constant import IN, OUT

Points = get_model('mypoints', 'Points')
Coin = get_model('payment', 'Coin')


class PointsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Points
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
        amount = int(validated_data.get('amount', 0))
        points_amounts = user.account.points_amounts
        points_active = points_amounts['total_active']

        if not amount or amount == 0:
            raise NotAcceptable(_("Poin harus lebih besar dari 0"))

        if amount > points_active:
            raise NotAcceptable(_("Poin tidak cukup. Poin Anda saat ini %s" % points_active))

        validated_data['transaction_type'] = OUT
        validated_data['description'] = _("Penukaran ke Coin sebesar %s" % (amount))
        obj = Points.objects.create(**validated_data)

        if obj:
            caused_content_type = ContentType.objects \
                .get_for_model(obj, for_concrete_model=False)

            description = _("Penukaran Poin sebesar %s" % amount)
            Coin.objects.create(
                caused_object_id=obj.id, caused_content_type=caused_content_type,
                user=obj.user, transaction_type=IN, amount=amount,
                description=description)
    
        return obj
