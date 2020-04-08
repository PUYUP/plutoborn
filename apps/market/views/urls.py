from django.urls import path

from apps.market.views.bundle import BundleListView, BundleDetailView
from apps.market.views.voucher import VoucherRedeemListView
from apps.market.views.affiliate import AffiliateView, AffiliateCaptureView

urlpatterns = [
    path('bundle/', BundleListView.as_view(), name='bundle_list'),
    path('bundle/<uuid:bundle_uuid>/', BundleDetailView.as_view(), name='bundle_detail'),

    path('voucher/', VoucherRedeemListView.as_view(), name='voucher_redeem_list'),
    path('affiliate/', AffiliateView.as_view(), name='affiliate'),
    path('affiliate/ref-<str:affiliate_code>/', AffiliateCaptureView.as_view(), name='affiliate_capture'),
]
