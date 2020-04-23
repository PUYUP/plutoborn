from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model
from apps.tryout.utils.constant import ACTIVE, HOLD
from apps.market.utils.constant import ACCEPT, HOLD as HOLD_M
from apps.payment.utils.general import money_to_coin
from apps.payment.utils.constant import OUT, IN

Acquired = get_model('tryout', 'Acquired')
Coin = get_model('payment', 'Coin')
BoughtProof = get_model('market', 'BoughtProof')


def bought_save_handler(sender, instance, created, **kwargs):
    packets = instance.bundle.packet.all()
    packet_ids = packets.values_list('id', flat=True)

    if created:
        coin_amount = instance.bundle.coin_amount
        description = _("Pembelian %s" % instance.bundle.label)

        # create acquired
        if packets.exists():
            packet_objects = list()
            for item in packets:
                # if premium make status auto-set to 'active'
                if coin_amount > 0:
                    acquired_status = ACTIVE
                else:
                    acquired_status = HOLD

                obj = Acquired(user=instance.user, packet=item, status=acquired_status)
                packet_objects.append(obj)

            if packet_objects:
                Acquired.objects.bulk_create(packet_objects, ignore_conflicts=True)

        # create coin
        caused_content_type = ContentType.objects \
            .get_for_model(instance.bundle, for_concrete_model=False)

        Coin.objects.create(user=instance.user, amount=coin_amount,
                            caused_object_id=instance.bundle.id, caused_content_type=caused_content_type,
                            transaction_type=OUT, description=description)

        # create proof
        if not coin_amount or coin_amount < 0:
            BoughtProof.objects.create(user=instance.user, bought=instance)

    if not created:
        # bought change status to active
        # we make all packet behind the bought will be active
        if instance.status == ACCEPT:
            acquireds = Acquired.objects.filter(user=instance.user, status=HOLD, packet__in=packet_ids)
            if acquireds:
                acquireds.update(status=ACTIVE)

        if instance.status == HOLD_M:
            acquireds = Acquired.objects.filter(user=instance.user, status=ACTIVE, packet__in=packet_ids)
            if acquireds:
                acquireds.update(status=HOLD)


def bought_delete_handler(sender, instance, using, **kwargs):
    # clear Acquired packets from user
    packets = instance.bundle.packet.all()
    user = instance.user

    if packets.exists():
        packet_ids = packets.values_list('id', flat=True)
        acquireds = user.acquireds.filter(packet_id__in=packet_ids)
        if acquireds:
            acquireds.delete()


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
