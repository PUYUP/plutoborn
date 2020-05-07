import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# Google Drive
from gdstorage.storage import GoogleDriveStorage

from apps.market.utils.constant import (
    BUNDLE_STATUS, PUBLISHED, SIMULATION_TYPE, GENERAL, HOLD, ACCEPT, BOUGHT_STATUS)

User = get_user_model()
gd_storage = GoogleDriveStorage()
gd_storage._get_or_create_folder('moorid')


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
        ordering = ['-date_created']
        verbose_name = _("Bundel")
        verbose_name_plural = _("Bundel")

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


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


class AbstractBought(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE,
                             related_name='boughts')
    bundle = models.ForeignKey('market.Bundle', on_delete=models.CASCADE,
                               related_name='boughts')

    status = models.CharField(max_length=255, choices=BOUGHT_STATUS, default=ACCEPT, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        ordering = ['-date_created']
        verbose_name = _("Dibeli")
        verbose_name_plural = _("Dibeli")

    def __str__(self):
        return self.bundle.label

    def save(self, *args, **kwargs):
        if not self.pk and self.bundle.coin_amount == 0:
            self.status = HOLD

        super().save(*args, **kwargs)


class AbstractBoughtProofRequirement(models.Model):
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=1)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        unique_together = ('label',)
        verbose_name = _("Bought Proof Requirement")
        verbose_name_plural = _("Bought Proof Requirements")

    def __str__(self):
        return self.label


class AbstractBoughtProof(models.Model):
    bought = models.OneToOneField(
        'market.Bought', on_delete=models.CASCADE, related_name='bought_proof')
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='bought_proofs')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        unique_together = ('bought',)
        verbose_name = _("Bought Proof")
        verbose_name_plural = _("Bought Proofs")

    def __str__(self):
        return self.bought.bundle.label


class AbstractBoughtProofDocument(models.Model):
    _UPLOAD_TO_IMG = 'images/proof'
    _UPLOAD_TO_FILE = 'files/proof'

    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='bought_proof_documents')
    bought_proof = models.ForeignKey(
        'market.BoughtProof', on_delete=models.CASCADE, related_name='bought_proof_documents')
    bought_proof_requirement = models.ForeignKey(
        'market.BoughtProofRequirement', on_delete=models.SET_NULL, null=True,
        related_name='bought_proof_documents')

    value_image = models.ImageField(upload_to=_UPLOAD_TO_IMG, storage=gd_storage,
                                    max_length=500, blank=True)
    value_file = models.FileField(upload_to=_UPLOAD_TO_FILE, storage=gd_storage,
                                  max_length=500, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'market'
        verbose_name = _("Bought Proof Document")
        verbose_name_plural = _("Bought Proof Documents")

    def __str__(self):
        return self.bought_proof.bought.bundle.label

    def save(self, *args, **kwargs):
        if self.bought_proof:
            self.user = self.bought_proof.user

        super().save(*args, **kwargs)
