import uuid
import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from apps.tryout.utils.constant import (
    CLASSIFICATION, RIGHT_CHOICE, EDUCATION_LEVEL, PACKET_STATUS, DRAFT, ALL, SCORE,
    SCORING_TYPE, TRUE_FALSE_NONE)


# Create your models here.
class AbstractTheory(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'parent__isnull': True},
        help_text=_("Jika ini sub-materi, pilih materi utamanya."))

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scoring_type = models.CharField(choices=SCORING_TYPE, default=TRUE_FALSE_NONE, max_length=255,
                                    null=True)
    true_score = models.IntegerField(null=True)
    false_score = models.IntegerField(null=True)
    none_score = models.IntegerField(null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True, help_text=_("Durasi dalam menit."))

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Materi')
        verbose_name_plural = _('Materi')

    def __str__(self):
        return self.label


class AbstractPacket(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    label = models.CharField(max_length=255, verbose_name=_("Nama Paket"))
    description = models.TextField(blank=True, verbose_name=_("Keterangan"))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Tanggal dan Jam Mulai"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Tanggal dan Jam Selesai"))
    duration = models.IntegerField(blank=True, null=True, help_text=_("Durasi dalam menit."),
                                   verbose_name=_("Durasi"))
    chance = models.IntegerField(verbose_name=_("Boleh Mengulang?"),
                                 help_text=_("Kesempatan mengulang. 0 untuk tidak ada pengulangan"))
    passed_score = models.IntegerField(verbose_name=_("Minimal Skor Lolos"))
    classification = models.CharField(choices=CLASSIFICATION, verbose_name=_("Jenis"), default=SCORE, max_length=255)
    education_level = models.CharField(choices=EDUCATION_LEVEL, null=True, blank=True,
                                              verbose_name=_("Jenjang"), default=ALL, max_length=255)
    status = models.CharField(choices=PACKET_STATUS, null=True, default=DRAFT, max_length=255)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Paket')
        verbose_name_plural = _('Paket')

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        start_date = self.start_date
        duration = self.duration

        if start_date and duration:
            self.end_date = start_date + datetime.timedelta(minutes=duration)
        super().save(*args, **kwargs)


class AbstractQuestion(models.Model):
    packet = models.ForeignKey(
        'tryout.Packet',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_("Paket"))
    theory = models.ForeignKey(
        'tryout.Theory',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='questions',
        limit_choices_to={'parent__isnull': True},
        verbose_name=_("Materi"))
    sub_theory = models.ForeignKey(
        'tryout.Theory',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='+',
        limit_choices_to={'parent__isnull': False},
        verbose_name=_("Sub Materi"))

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numbering = models.IntegerField(null=True, editable=False)
    numbering_local = models.IntegerField(null=True, editable=False)
    label = models.CharField(max_length=500, verbose_name=_("Judul Pertanyaan"))
    score = models.IntegerField(blank=True, null=True, verbose_name=_("Skor"))
    description = models.TextField(blank=True, verbose_name=_("Keterangan Tambahan"))
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Pertanyaan')
        verbose_name_plural = _('Pertanyaan')

    def __str__(self):
        return self.label

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        if not self.pk:
            questions = self.__class__.objects \
                .prefetch_related('packet', 'theory', 'sub_theory') \
                .select_related('packet', 'theory', 'sub_theory')

            question_numbering = questions.filter(packet=self.packet).count()
            question_numbering_local = questions.filter(packet=self.packet, theory=self.theory).count()

            self.numbering = question_numbering + 1
            self.numbering_local = question_numbering_local + 1
        super().save(*args, **kwargs)


class AbstractChoice(models.Model):
    packet = models.ForeignKey(
        'tryout.Packet',
        on_delete=models.CASCADE,
        editable=False, null=True,
        related_name='choices',
        verbose_name=_("Paket"))
    question = models.ForeignKey(
        'tryout.Question',
        related_name='choices',
        on_delete=models.CASCADE)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=1, verbose_name=_("Pilihan"))
    label = models.CharField(max_length=500, verbose_name=_("Jawaban"))
    score = models.IntegerField(blank=True, null=True, verbose_name=_("Skor"))
    description = models.TextField(blank=True, verbose_name=_("Keterangan"))
    explanation = models.TextField(blank=True, verbose_name=_("Penjelasan Jawaban"))
    right_choice = models.BooleanField(default=False, verbose_name=_("Ini Jawaban Benar"))
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Pilihan')
        verbose_name_plural = _('Pilihan')

    def __str__(self):
        return self.label

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.identifier = self.identifier.capitalize()
        self.packet = self.question.packet
        super().save(*args, **kwargs)


class AbstractAnswer(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='answers')
    packet = models.ForeignKey(
        'tryout.Packet',
        on_delete=models.CASCADE,
        editable=False,
        related_name='answers')
    question = models.ForeignKey(
        'tryout.Question',
        on_delete=models.CASCADE,
        related_name='answers')
    choice = models.ForeignKey(
        'tryout.Choice',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='answers')
    simulation = models.ForeignKey(
        'tryout.Simulation',
        on_delete=models.CASCADE, null=True,
        related_name='answers')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    right_choice = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Jawaban')
        verbose_name_plural = _('Jawaban')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.choice:
            self.right_choice = self.choice.right_choice

        self.packet = self.question.packet
        super().save(*args, **kwargs)


class AbstractAcquired(models.Model):
    """This auto fill after user Bought a Bundle"""
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='acquireds')
    packet = models.ForeignKey(
        'tryout.Packet',
        on_delete=models.CASCADE,
        related_name='acquireds')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        unique_together = ('user', 'packet',)
        verbose_name = _('Paket Dibeli')
        verbose_name_plural = _('Paket Dibeli')

    def __str__(self):
        return self.packet.label
