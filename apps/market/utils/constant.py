from django.utils.translation import ugettext_lazy as _

PUBLISHED = 'published'
DRAFT = 'draft'
BUNDLE_STATUS = (
    (PUBLISHED, _("Terbit")),
    (DRAFT, _("Konsep")),
)


VOUCHER_ACTIVE = 'active'
VOUCHER_INACTIVE = 'inactive'
VOUCHER_EXPIRED = 'expired'
VOUCHER_STATUS = (
    (VOUCHER_ACTIVE, _("Aktif")),
    (VOUCHER_INACTIVE, _("Tidak Aktif")),
    (VOUCHER_EXPIRED, _("Expired")),
)

GENERAL = 'general'
NATIONAL = 'national'
SIMULATION_TYPE = (
    (GENERAL, _("Umum")),
    (NATIONAL, _("Nasional")),
)


ACCEPT = 'accept'
HOLD = 'hold'
BOUGHT_STATUS = (
    (ACCEPT, _("Accept")),
    (HOLD, _("Hold"))
)
