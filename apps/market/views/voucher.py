from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Case, When, Value, BooleanField
from django.core.exceptions import ObjectDoesNotExist

from utils.generals import get_model
from apps.market.utils.constant import PUBLISHED

VoucherRedeem = get_model('market', 'VoucherRedeem')


class VoucherRedeemListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/voucher-acquired-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        vouchers = user.voucher_redeems \
            .prefetch_related(Prefetch('voucher'), Prefetch('user')) \
            .select_related('voucher', 'user')

        self.context['vouchers'] = vouchers
        return render(request, self.template_name, self.context)
