from django.urls import path

from apps.market.views.bundle import BundleListView, BundleDetailView
from apps.market.views.voucher import VoucherRedeemListView
from apps.market.views.affiliate import (
    AffiliateView, AffiliateListView, AffiliateCaptureView,
    CommissionListView)
from apps.market.views.proof import BoughtProofView

urlpatterns = [
    path('bundle/', BundleListView.as_view(), name='bundle_list'),
    path('bundle/enrolled/', BundleListView.as_view(), name='bundle_list_enrolled'),
    path('bundle/<uuid:bundle_uuid>/', BundleDetailView.as_view(), name='bundle_detail'),
    path('bundle/<uuid:bundle_uuid>/proof/', BoughtProofView.as_view(), name='bought_proof'),

    path('voucher/', VoucherRedeemListView.as_view(), name='voucher_redeem_list'),
    path('affiliate/', AffiliateView.as_view(), name='affiliate'),
    path('affiliate/all/', AffiliateListView.as_view(), name='affiliate_list'),
    path('affiliate/ref-<str:affiliate_code>/', AffiliateCaptureView.as_view(), name='affiliate_capture'),
    path('affiliate/commission/', CommissionListView.as_view(), name='affiliate_commission'),
]
