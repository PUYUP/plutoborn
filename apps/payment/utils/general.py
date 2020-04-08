from django.conf import settings

def money_to_coin(money=0):
    if money == 0:
        return 0

    y = money * settings.COIN_EXCHANGE
    return int(y)
