from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Case, When, Value, BooleanField
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
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

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(vouchers, settings.PAGINATION_PER_PAGE)

        try:
            vouchers_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            vouchers_pagination = paginator.page(1)
        except EmptyPage:
            vouchers_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, vouchers, vouchers_pagination, page_num, paginator)

        self.context['vouchers'] = vouchers
        self.context['vouchers_pagination'] = vouchers_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
