from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model
from apps.payment.utils.general import money_to_coin
from apps.payment.utils.constant import OUT, IN

Acquired = get_model('tryout', 'Acquired')
Coin = get_model('payment', 'Coin')


def bought_handler(sender, instance, created, **kwargs):
    if created:
        coin_amount = instance.bundle.coin_amount
        packets = instance.bundle.packet.all()
        description = _("Pembelian %s" % instance.bundle.label)

        # create acquired
        if packets.exists():
            packet_objects = list()
            for item in packets:
                obj = Acquired(user=instance.user, packet=item)
                packet_objects.append(obj)

            if packet_objects:
                Acquired.objects.bulk_create(packet_objects, ignore_conflicts=True)

        # create coin
        caused_content_type = ContentType.objects \
            .get_for_model(instance.bundle, for_concrete_model=False)

        Coin.objects.create(user=instance.user, amount=coin_amount,
                            caused_object_id=instance.bundle.id, caused_content_type=caused_content_type,
                            transaction_type=OUT, description=description)


def voucher_redeem_handler(sender, instance, created, **kwargs):
    if created:
        coin_amount = instance.voucher.coin_amount
        description = _("Penukaran Voucher %s dengan kode %s" % (instance.voucher.label, instance.voucher.code))

        # create coin
        caused_content_type = ContentType.objects \
            .get_for_model(instance.voucher, for_concrete_model=False)

        Coin.objects.create(user=instance.user, amount=coin_amount,
                            caused_object_id=instance.voucher.id, caused_content_type=caused_content_type,
                            transaction_type=IN, description=description)
