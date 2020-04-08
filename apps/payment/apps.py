from django.apps import AppConfig
from django.db.models.signals import post_save


class PaymentConfig(AppConfig):
    name = 'apps.payment'

    def ready(self):
        from utils.generals import get_model
        from apps.payment.signals import topup_handler

        TopUp = get_model('payment', 'TopUp')
        post_save.connect(topup_handler, sender=TopUp, dispatch_uid='topup_signal')
