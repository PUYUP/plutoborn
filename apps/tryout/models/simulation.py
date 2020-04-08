import uuid
import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from apps.market.utils.constant import SIMULATION_TYPE, GENERAL


class AbstractSimulation(models.Model):
    """Mapping acquired with user. With this we can use chance feature"""
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='simulations')
    acquired = models.ForeignKey(
        'tryout.Acquired',
        on_delete=models.CASCADE,
        related_name='simulations')
    packet = models.ForeignKey(
        'tryout.Packet',
        on_delete=models.CASCADE,
        null=True, editable=False,
        related_name='simulations')
    program_study = models.ManyToManyField(
        'tryout.ProgramStudy', blank=True,
        related_name='simulations')

    duration_half = models.IntegerField(blank=True, null=True, editable=False)
    start_date = models.DateTimeField(blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True)
    chance = models.IntegerField(default=1)
    is_done = models.BooleanField(default=False)

    simulation_type = models.CharField(choices=SIMULATION_TYPE, default=GENERAL, max_length=255, null=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Paket Dikerjakan')
        verbose_name_plural = _('Paket Dikerjakan')

    def __str__(self):
        return self.packet.label

    def save(self, *args, **kwargs):
        self.packet = self.acquired.packet
        self.duration_half = self.packet.duration

        # strict is_done = False only to one object
        # if current make is_done = True then mark all objects to False
        old_simulations = self.__class__.objects.filter(user=self.user, packet=self.packet)
        old_simulations_not_done = old_simulations.filter(is_done=False)
        if not self.is_done and old_simulations_not_done.exists():
            old_simulations_not_done.update(is_done=True)

        if not self.pk:
            self.start_date = timezone.now()
            self.chance = old_simulations.count() + 1

        super().save(*args, **kwargs)


class AbstractProgramStudy(models.Model):
    name = models.CharField(max_length=255)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Prodi')
        verbose_name_plural = _('Prodi')

    def __str__(self):
        return self.name
