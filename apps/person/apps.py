from django.apps import AppConfig
from django.db.models.signals import post_save


class PersonConfig(AppConfig):
    name = 'apps.person'

    def ready(self):
        from utils.generals import get_model
        from django.contrib.auth.models import User
        from apps.person.signals import (
            user_handler, otpcode_handler)

        OTPCode = get_model('person', 'OTPCode')

        post_save.connect(user_handler, sender=User, dispatch_uid='user_signal')
        post_save.connect(otpcode_handler, sender=OTPCode, dispatch_uid='otpcode_signal')
