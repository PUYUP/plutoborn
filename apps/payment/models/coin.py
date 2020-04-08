import uuid

from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.payment.utils.constant import (
    TRANSACTION_COIN_TYPE,
    IN, OUT, SETTLEMENT)

User = get_user_model()


class AbstractCoin(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='coins')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    transaction_type = models.CharField(
        choices=TRANSACTION_COIN_TYPE, default=IN, max_length=255)
    amount = models.BigIntegerField()
    description = models.TextField(null=True, blank=True)

    _LIMIT = models.Q(app_label='payment', model='topup') \
        | models.Q(app_label='mypoints', model='points') \
        | models.Q(app_label='market', model='voucherredeem')
    caused_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to=_LIMIT)
    caused_object_id = models.PositiveIntegerField(null=True, blank=True)
    caused_content_object = GenericForeignKey('caused_content_type', 'caused_object_id')

    class Meta:
        abstract = True
        app_label = 'payment'
        ordering = ['-date_created']
        verbose_name = _("Coin")
        verbose_name_plural = _("Coins")

    def __str__(self):
        return self.get_transaction_type_display()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
