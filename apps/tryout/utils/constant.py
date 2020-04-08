from django.utils.translation import ugettext_lazy as _

LIVE = 'live'
SCORE = 'score'
CLASSIFICATION = (
    (LIVE, _("Live")),
    (SCORE, _("Skor")),
)


TRUE = 'true'
FALSE = 'false'
RIGHT_CHOICE = (
    (FALSE, _("Salah")),
    (TRUE, _("Benar")),
)


SD = 'sd'
SMP = 'smp'
SMA = 'sma'
COLLEGE = 'college'
ALL = 'all'
EDUCATION_LEVEL = (
    (SD, _("Sekolah Dasar")),
    (SMP, _("Sekolah Menengah Pertama")),
    (SMA, _("Sekolah Menengah Atas")),
    (COLLEGE, _("Perguruan Tinggi")),
    (ALL, _("Semua")),
)


DRAFT = 'draft'
REVIEWED = 'reviewed'
PUBLISHED = 'published'
PACKET_STATUS = (
    (DRAFT, _("Konsep")),
    (REVIEWED, _("Ditinjau")),
    (PUBLISHED, _("Terbit")),
)


TRUE_FALSE_NONE = 'true_false_none'
PREFERENCE = 'preference'
SCORING_TYPE = (
    (TRUE_FALSE_NONE, _("Benar, Salah, Kosong")),
    (PREFERENCE, _("Menurut Pilihan")),
)
