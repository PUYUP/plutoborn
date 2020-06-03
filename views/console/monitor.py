from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q, F, Sum, Case, When, Value, Subquery, OuterRef, IntegerField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Coalesce

from utils.pagination import Pagination
from utils.generals import get_model
from apps.payment.utils.constant import (
    TRANSACTION_COIN_TYPE,
    IN, OUT, SETTLEMENT)

User = get_user_model()
TopUp = get_model('payment', 'TopUp')


class UserMonitorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/monitor/user.html'
    context = dict()

    def get(self, request):
        user_subqs = User.objects.filter(pk=OuterRef('id'))
        users = User.objects \
            .annotate(
                total_topup=Coalesce(Subquery(
                    user_subqs.annotate(total_topup=Sum('topups__payment_amount')).values('total_topup'),
                    output_field=IntegerField()
                ), 0),

                # Calculate coin
                total_coin_in=Coalesce(Subquery(
                    user_subqs.filter(coins__transaction_type=IN).annotate(total_coin=Sum('coins__amount')).values('total_coin'),
                    output_field=IntegerField()
                ), 0),
                total_coin_out=Coalesce(Subquery(
                    user_subqs.filter(coins__transaction_type=OUT).annotate(total_coin=Sum('coins__amount')).values('total_coin'),
                    output_field=IntegerField()
                ), 0),
                total_coin_active=F('total_coin_in') - F('total_coin_out'),

                # Calculate poin
                total_points_in=Coalesce(Subquery(
                    user_subqs.filter(points__transaction_type=IN).annotate(total_points=Sum('points__amount')).values('total_points'),
                    output_field=IntegerField()
                ), 0),
                total_points_out=Coalesce(Subquery(
                    user_subqs.filter(points__transaction_type=OUT).annotate(total_points=Sum('points__amount')).values('total_points'),
                    output_field=IntegerField()
                ), 0),
                total_points_active=F('total_points_in') - F('total_points_out')
            ) \
            .filter(account__isnull=False) \
            .order_by('-total_topup')
        
        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(users, settings.PAGINATION_PER_PAGE)

        try:
            users_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            users_pagination = paginator.page(1)
        except EmptyPage:
            users_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, users, users_pagination, page_num, paginator)

        self.context['users'] = users
        self.context['users_total'] = users.count()
        self.context['users_pagination'] = users_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
