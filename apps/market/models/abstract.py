import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.market.utils.constant import (
    BUNDLE_STATUS, PUBLISHED, SIMULATION_TYPE, GENERAL)

User = get_user_model()


# Create your models here.
class AbstractBundle(models.Model):
    packet = models.ManyToManyField(
        'tryout.Packet',
        limit_choices_to={'status': PUBLISHED})

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    label = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    coin_amount = models.BigIntegerField(help_text=_("Jika gratis isi dengan nol."))
    status = models.CharField(choices=BUNDLE_STATUS, default=PUBLISHED, max_length=255)
    simulation_type = models.CharField(choices=SIMULATION_TYPE, default=GENERAL, max_length=255, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Tanggal dan Jam Mulai"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Tanggal dan Jam Selesai"))

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Bundel")
        verbose_name_plural = _("Bundel")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AbstractBought(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='boughts')
    bundle = models.ForeignKey(
        'market.Bundle',
        on_delete=models.CASCADE,
        related_name='boughts')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Dibeli")
        verbose_name_plural = _("Dibeli")

    def __str__(self):
        return self.bundle.label


class AbstractBundlePasswordPassed(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='bundle_passwords')
    bundle = models.ForeignKey(
        'market.Bundle',
        on_delete=models.CASCADE,
        related_name='bundle_passwords')

    password = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Bundle Password Passed")
        verbose_name_plural = _("Bundle Password Passeds")

    def __str__(self):
        return self.bundle.label
