from django.db.models import Q

from utils.generals import get_model
# Celery task
from apps.person.tasks import send_otp_email

Account = get_model('person', 'Account')
Profile = get_model('person', 'Profile')
Role = get_model('person', 'Role')


def user_handler(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, email=instance.email)
        Profile.objects.create(user=instance)
        Role.objects.create(user=instance)

    if not created:
        instance.account.email = instance.email
        instance.account.save()


def otpcode_handler(sender, instance, created, **kwargs):
    if instance.email:
        data = {
            'email': getattr(instance, 'email', None),
            'otp_code': getattr(instance, 'otp_code', None)
        }
        send_otp_email.delay(data)

    if created:
        oldest = instance.__class__.objects \
            .filter(
                Q(identifier=instance.identifier),
                Q(is_used=False), Q(is_expired=False),
                Q(email=instance.email), Q(telephone=instance.telephone)) \
            .exclude(otp_code=instance.otp_code)

        if oldest:
            oldest.update(is_expired=True)
