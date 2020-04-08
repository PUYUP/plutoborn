from django.urls import path

from apps.payment.views.coin import CoinView
from apps.payment.views.topup import TopUpDetailView

urlpatterns = [
    path('coin/', CoinView.as_view(), name='coin'),
    path('topup/<uuid:topup_uuid>/', TopUpDetailView.as_view(), name='topup_detail'),
]
