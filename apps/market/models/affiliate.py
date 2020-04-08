import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model, random_string
from apps.market.utils.constant import VOUCHER_ACTIVE, VOUCHER_STATUS
from apps.payment.utils.constant import (
    TRANSACTION_COIN_TYPE, IN, OUT)


# Create your models here.
class AbstractAffiliate(models.Model):
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='affiliate')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    code = models.CharField(max_length=255, verbose_name=_("Kode Referral"), editable=False)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Affiliate")
        verbose_name_plural = _("Affiliates")

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.code = '%s-%s' % (random_string(), self.user.id)
        super().save(*args, **kwargs)


class AbstractAffiliateAcquired(models.Model):
    affiliate = models.ForeignKey(
        'market.Affiliate',
        on_delete=models.CASCADE,
        related_name='affiliate_acquireds')
    user_acquired = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='affiliate_user_acquireds')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Affiliate Acquired")
        verbose_name_plural = _("Affiliate Acquireds")

    def __str__(self):
        return self.affiliate.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AbstractAffiliateCommission(models.Model):
    # who buy Bundle
    creator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='commission_creators')

    # who user target
    affiliator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='commission_affiliators',
        null=True, blank=True)

    amount = models.BigIntegerField()
    description = models.TextField(null=True, blank=True)
    transaction_type = models.CharField(
        choices=TRANSACTION_COIN_TYPE, default=IN, max_length=255)

    # this target to Bundle
    _LIMIT = models.Q(app_label='tryout', model='bundle')
    caused_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to=_LIMIT)
    caused_object_id = models.PositiveIntegerField(null=True, blank=True)
    caused_content_object = GenericForeignKey('caused_content_type', 'caused_object_id')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Affiliate Commission")
        verbose_name_plural = _("Affiliate Commissions")

    def __str__(self):
        return self.affiliate.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AbstractAffiliateCapture(models.Model):
    code = models.CharField(max_length=255)
    ipaddr = models.CharField(max_length=255)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Affiliate Capture")
        verbose_name_plural = _("Affiliate Captures")

    def __str__(self):
        return self.ipaddr
