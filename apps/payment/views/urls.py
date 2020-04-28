from django.urls import path

from apps.payment.views.coin import CoinView
from apps.payment.views.topup import TopUpView, TopUpDetailView
from apps.payment.views.index import PaymentView

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment/coin/', CoinView.as_view(), name='payment_coin'),
    path('payment/topup/', TopUpView.as_view(), name='payment_topup'),
    path('payment/topup/<uuid:topup_uuid>/', TopUpDetailView.as_view(), name='topup_detail'),
]
