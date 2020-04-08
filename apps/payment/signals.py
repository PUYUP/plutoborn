from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model
from apps.payment.utils.general import money_to_coin
from apps.payment.utils.constant import SETTLEMENT, CAPTURE, IN

Coin = get_model('payment', 'Coin')


def topup_handler(sender, instance, created, **kwargs):
    if created:
        if instance.payment_status == SETTLEMENT or instance.payment_status == CAPTURE:
            # convert to coin
            amount = money_to_coin(instance.payment_amount)
            description = _("Topup sejumlah Rp %s" % instance.payment_amount)
            caused_content_type = ContentType.objects \
                .get_for_model(instance, for_concrete_model=False)

            Coin.objects.create(
                caused_object_id=instance.id, caused_content_type=caused_content_type,
                user=instance.user, transaction_type=IN, amount=amount,
                description=description)
