import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from utils.generals import get_model
from apps.market.utils.constant import VOUCHER_ACTIVE, VOUCHER_STATUS

User = get_user_model()


# Create your models here.
class AbstractVoucher(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vouchers')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    code = models.CharField(max_length=10, verbose_name=_("Kode Voucher"))
    label = models.CharField(max_length=500, verbose_name=_("Nama Voucher"))
    description = models.TextField(blank=True)
    coin_amount = models.BigIntegerField()
    max_usage = models.BigIntegerField(verbose_name=_("Boleh Digunakan Sebanyak?"))
    max_usage_per_user = models.BigIntegerField(verbose_name=_("Per User Boleh Menggunakan Sebanyak?"))
    start_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=VOUCHER_STATUS, default=VOUCHER_ACTIVE, max_length=255)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AbstractVoucherRedeem(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='voucher_redeems')
    voucher = models.ForeignKey(
        'market.Voucher',
        on_delete=models.CASCADE,
        related_name='voucher_redeems')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Voucher Redeem")
        verbose_name_plural = _("Voucher Redeems")

    def __str__(self):
        return self.voucher.label

    def clean(self):
        if not self.pk:
            if self.voucher.start_date > timezone.now():
                raise ValidationError(_("Voucher akan berlaku pada %s." % self.voucher.start_date))

            if self.voucher.finish_date < timezone.now():
                raise ValidationError(_("Voucher telah berakhir."))

            olds = self.__class__.objects.filter(voucher__code=self.voucher.code)
            if olds.exists() and olds.count() >= self.voucher.max_usage:
                raise ValidationError(_("Penggunaan mencapai batas %s" % self.voucher.max_usage))

            olds_per_user = self.__class__.objects.filter(voucher__code=self.voucher.code, user=self.user)
            if olds_per_user.exists() and olds_per_user.count() >= self.voucher.max_usage_per_user:
                raise ValidationError(_("Penggunaan per user mencapai batas %s" % self.voucher.max_usage_per_user))

    def save(self, *args, **kwargs):
        # validate!
        self.clean()

        super().save(*args, **kwargs)
