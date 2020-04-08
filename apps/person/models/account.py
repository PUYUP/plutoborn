import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum, Q, IntegerField
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.validators import validate_email

from utils.generals import get_model
from apps.person.utils.constant import EMAIL_VALIDATION, TELEPHONE_VALIDATION
from apps.payment.utils.constant import IN, OUT


# Create your models here.
class AbstractAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='account')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(blank=True, null=True, max_length=14)

    email_verified = models.BooleanField(default=False, null=True)
    telephone_verified = models.BooleanField(default=False, null=True)

    class Meta:
        abstract = True
        app_label = 'person'
        ordering = ['-user__date_joined']
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")

    def __str__(self):
        return self.user.username

    @property
    def coin_amounts(self):
        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        coins_total = self.user.coins.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out)
        return coins_total

    @property
    def points_amounts(self):
        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        points_total = self.user.points.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out)
        return points_total

    @property
    def commission_amounts(self):
        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        commissions_total = self.user.commission_affiliators.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out)
        return commissions_total

    def validate_email(self, *args, **kwargs):
        if self.email_verified == True:
            raise ValidationError(_("Email has verified."))

        OTPCode = get_model('person', 'OTPCode')
        try:
            OTPCode.objects \
                .filter(email=self.email, is_used=True, identifier=EMAIL_VALIDATION) \
                .latest('date_created')
        except ObjectDoesNotExist:
            raise ValidationError(_("OTP code invalid."))
        self.email_verified = True
        self.save()

    def validate_telephone(self, *args, **kwargs):
        if self.telephone_verified == True:
            raise ValidationError(_("Telephone has verified."))

        OTPCode = get_model('person', 'OTPCode')
        try:
            OTPCode.objects \
                .filter(telephone=self.telephone, is_used=True, identifier=TELEPHONE_VALIDATION) \
                .latest('date_created')
        except ObjectDoesNotExist:
            raise ValidationError(_("OTP code invalid."))
        self.telephone_verified = True
        self.save()


class AbstractProfile(models.Model):
    _UPLOAD_TO = '%s/images/user' % settings.MEDIA_ROOT

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)

    school_origin = models.CharField(verbose_name=_("Asal Sekolah"), max_length=255, blank=True, null=True)
    graduation_year = models.IntegerField(verbose_name=_("Tahun Kelulusan"), null=True, blank=True)
    born_place = models.CharField(verbose_name=_("Tempat Lahir"), max_length=255, blank=True, null=True)
    born_date = models.DateField(verbose_name=_("Tanggal Lahir"), null=True, blank=True)
    whatsapp = models.CharField(verbose_name=_("Nomor WhatsApp"), max_length=255, blank=True, null=True)
    instagram = models.CharField(verbose_name=_("Akun Instagram"), max_length=255, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to=_UPLOAD_TO, max_length=500, null=True, blank=True)

    class Meta:
        abstract = True
        app_label = 'person'
        ordering = ['-user__date_joined']
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username

    @property
    def is_empty(self):
        x = self.__class__.objects \
            .filter(
                user_id=self.user.id,
                school_origin__isnull=True,
                graduation_year__isnull=True,
                born_place__isnull=True,
                born_date__isnull=True,
                whatsapp__isnull=True,
                instagram__isnull=True,
            )

        return x.exists()
