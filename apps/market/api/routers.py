from django.urls import path, include

# THIRD PARTY
from rest_framework.routers import DefaultRouter

# LOCAL
from .bought.views import BoughtApiView
from .voucher.views import VoucherRedeemApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('boughts', BoughtApiView, basename='bought')
router.register('voucher-redeems', VoucherRedeemApiView, basename='voucher_redeem')

app_name = 'market'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
