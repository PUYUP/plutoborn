import uuid
import datetime

from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from utils.generals import FileSystemStorageExtend, get_model
from apps.tryout.utils.constant import (
    CLASSIFICATION, RIGHT_CHOICE, EDUCATION_LEVEL, PACKET_STATUS, DRAFT, ALL, SCORE,
    SCORING_TYPE, TRUE_FALSE_NONE, HOLD, ACQUIRED_STATUS)


def directory_image_path(instance, filename):
    fs = FileSystemStorageExtend()
    year = datetime.date.today().year
    month = datetime.date.today().month
    filename = fs.generate_filename(filename, instance=instance)

    # Will be 'files/2019/10/filename.jpg
    return 'images/{0}/{1}/{2}'.format(year, month, filename)


def directory_file_path(instance, filename):
    fs = FileSystemStorageExtend()
    year = datetime.date.today().year
    month = datetime.date.today().month
    filename = fs.generate_filename(filename, instance=instance)

    # Will be 'files/2019/10/filename.jpg
    return 'files/{0}/{1}/{2}'.format(year, month, filename)


# Create your models here.
class AbstractCategory(models.Model):
    label = models.CharField(max_length=255, verbose_name=_("Nama"), help_text=_("Contoh: Try Out UTBK"))
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        app_label = 'tryout'
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategori')

    def __str__(self):
        return self.label


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
    minimum_score = models.IntegerField(null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=False, null=True, help_text=_("Durasi dalam menit."))

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

    category = models.ForeignKey('tryout.Category', on_delete=models.SET_NULL, null=True)
    theories = models.ManyToManyField('tryout.Theory', related_name='packets', verbose_name=_("Materi"))
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
        # Count total duration!
        if self.pk and not self.duration:
            Question = get_model('tryout', 'Question')
            theories = Question.objects.filter(packet_id=self.pk) \
                .distinct() \
                .values('theory', 'theory__duration') \
                .aggregate(total_duration=Sum('theory__duration'))
            self.duration = theories['total_duration']

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
        blank=False, null=True,
        related_name='questions',
        limit_choices_to={'parent__isnull': True},
        verbose_name=_("Materi"))
    sub_theory = models.ForeignKey(
        'tryout.Theory',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='questions_sub_theory',
        limit_choices_to={'parent__isnull': False},
        verbose_name=_("Sub Materi"))

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    numbering = models.IntegerField(null=True, editable=False)
    numbering_local = models.IntegerField(null=True, editable=False)
    label = models.CharField(max_length=500, verbose_name=_("Judul Pertanyaan"))
    score = models.IntegerField(blank=True, null=True, verbose_name=_("Skor"))
    description = models.TextField(blank=True, verbose_name=_("Keterangan Tambahan"))
    explanation = models.TextField(blank=True, null=True, verbose_name=_("Pembahasan"))
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
    label = models.TextField(verbose_name=_("Jawaban"))
    score = models.IntegerField(blank=True, null=True, verbose_name=_("Skor"))
    description = models.TextField(blank=True, verbose_name=_("Keterangan"))
    explanation = models.TextField(blank=True, verbose_name=_("Pembahasan"))
    right_choice = models.BooleanField(default=False, verbose_name=_("Jawaban Benar"))
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

    status = models.CharField(choices=ACQUIRED_STATUS, default=HOLD, null=True,
                              max_length=255)
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


class AbstractAttachment(models.Model):
    uploader = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, related_name='attachments')

    value_image = models.ImageField(
        upload_to=directory_image_path,
        max_length=500, null=True, blank=True)
    value_file = models.FileField(
        upload_to=directory_file_path,
        max_length=500, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    caption = models.TextField(max_length=500, null=True, blank=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    # Generic relations
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        related_name='tryout_attachment',
        limit_choices_to=Q(app_label='tryout'), blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        app_label = 'tryout'
        ordering = ['-date_updated']
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        value = ''
        if self.value_image:
            value = self.value_image.url

        if self.value_file:
            value = self.value_file.url
        return value
