import uuid

from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from utils.generals import get_model
from apps.payment.utils.general import money_to_coin
from apps.payment.utils.constant import (
    PAYMENT_STATUS, PENDING, SETTLEMENT, CAPTURE, IN)

User = get_user_model()


class AbstractTopUp(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topups')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # this topup used or not
    # if payment captured is_used = True
    is_used = models.BooleanField(default=False)

    # payment gateway response (Midtrans)
    payment_order_id = models.CharField(max_length=255, null=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS, default=PENDING, max_length=255)
    payment_status_code = models.CharField(max_length=255, blank=True, null=True)
    payment_message = models.TextField(blank=True, null=True)
    payment_guide = models.CharField(max_length=500, blank=True, null=True)
    payment_type = models.CharField(max_length=255, blank=True, null=True)
    payment_amount = models.BigIntegerField()
    payment_created_date = models.DateTimeField(blank=True, null=True)
    payment_expired_date = models.DateTimeField(blank=True, null=True)
    payment_paid_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        app_label = 'payment'
        ordering = ['-date_created']
        verbose_name = _("Topup")
        verbose_name_plural = _("Topups")

    def __str__(self):
        return '%s %s' % (self.user.username, self.payment_amount)

    def save(self, *args, **kwargs):
        if self.payment_status == SETTLEMENT or self.payment_status == CAPTURE:
            self.is_used = True

        # will expired under 1 days from now
        if not self.pk and self.payment_created_date:
            self.payment_expired_date = self.payment_created_date + timezone.timedelta(days=1)
        super().save(*args, **kwargs)
