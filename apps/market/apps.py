from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class MarketConfig(AppConfig):
    name = 'apps.market'

    def ready(self):
        from utils.generals import get_model
        from apps.market.signals import (
            bought_save_handler, bought_delete_handler,
            voucher_redeem_handler)

        Bought = get_model('market', 'Bought')
        VoucherRedeem = get_model('market', 'VoucherRedeem')

        post_save.connect(bought_save_handler, sender=Bought,
                          dispatch_uid='bought_save_signal')
        post_delete.connect(bought_delete_handler, sender=Bought,
                            dispatch_uid='bought_delete_signal')
        post_save.connect(voucher_redeem_handler, sender=VoucherRedeem,
                          dispatch_uid='voucher_redeem_save_signal')
