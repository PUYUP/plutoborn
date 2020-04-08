import asyncio

from django.db.models import Q

from utils.generals import get_model
from apps.person.models.otp import _send_email

Account = get_model('person', 'Account')
Profile = get_model('person', 'Profile')
Role = get_model('person', 'Role')

_ASYNC_LOOP = asyncio.get_event_loop()


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
        _ASYNC_LOOP.run_in_executor(None, _send_email, instance)

    if created:
        oldest = instance.__class__.objects \
            .filter(
                Q(identifier=instance.identifier),
                Q(is_used=False), Q(is_expired=False),
                Q(email=instance.email), Q(telephone=instance.telephone)) \
            .exclude(otp_code=instance.otp_code)

        if oldest:
            oldest.update(is_expired=True)
