from django.utils.translation import ugettext_lazy as _

IN = 'in'
OUT = 'out'
TRANSACTION_COIN_TYPE = (
    (IN, _("Masuk")),
    (OUT, _("Keluar")),
)

CAPTURE = 'capture'
PENDING = 'pending'
SETTLEMENT = 'settlement'
CANCEL = 'cancel'
EXPIRED = 'expired'
PAYMENT_STATUS = (
    (CAPTURE, _("Capture")),
    (PENDING, _("Pending")),
    (SETTLEMENT, _("Settlement")),
    (CANCEL, _("Cancel")),
    (EXPIRED, _("Expired")),
)
