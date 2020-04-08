from .coin import *
from .topup import *

# PROJECT UTILS
from utils.generals import is_model_registered

__all__ = list()

# 0
if not is_model_registered('payment', 'TopUp'):
    class TopUp(AbstractTopUp):
        class Meta(AbstractTopUp.Meta):
            db_table = 'payment_topup'

    __all__.append('TopUp')


# 1
if not is_model_registered('payment', 'Coin'):
    class Coin(AbstractCoin):
        class Meta(AbstractCoin.Meta):
            db_table = 'payment_coin'

    __all__.append('Coin')
