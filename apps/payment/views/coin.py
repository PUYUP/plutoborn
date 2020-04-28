from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.db.models import Q, Prefetch, Sum, IntegerField, Case, When, Value, F
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
from apps.payment.utils.constant import IN, OUT, SETTLEMENT, CAPTURE, EXPIRED

User = get_user_model()


class CoinView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'payment/coin.html'
    context = dict()

    def get(self, request):
        user = request.user
        coins = user.coins.prefetch_related(Prefetch('user'), Prefetch('caused_content_type')) \
            .select_related('user', 'caused_content_type')
    
        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(coins, settings.PAGINATION_PER_PAGE)

        try:
            coins_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            coins_pagination = paginator.page(1)
        except EmptyPage:
            coins_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, coins, coins_pagination, page_num, paginator)

        self.context['SETTLEMENT'] = SETTLEMENT
        self.context['CAPTURE'] = CAPTURE
        self.context['EXPIRED'] = EXPIRED
        self.context['coins'] = coins
        self.context['coins_pagination'] = coins_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
