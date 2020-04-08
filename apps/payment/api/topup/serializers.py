from django.db import transaction

from rest_framework import serializers

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault

TopUp = get_model('payment', 'TopUp')


class TopUpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = TopUp
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        payment_amount = int(validated_data.pop('payment_amount', 0))

        # Create or get object
        obj = TopUp.objects.create(**validated_data, payment_amount=payment_amount)
        return obj
