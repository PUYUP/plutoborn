from django.views import View
from django.shortcuts import render
from django.db.models import Q, Prefetch, Sum, IntegerField, Case, When, Value, F
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.generals import get_model
from apps.payment.utils.constant import IN, OUT, SETTLEMENT, CAPTURE, EXPIRED

User = get_user_model()


class PaymentView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'payment/index.html'
    context = dict()

    def get(self, request):
        user = request.user
        coins = user.coins.prefetch_related(Prefetch('user'), Prefetch('caused_content_type')) \
            .select_related('user', 'caused_content_type')
        topups = user.topups.prefetch_related(Prefetch('user')) \
            .select_related('user')
    
        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        coins_total = coins.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out
        )
        coins_in_total = coins_total.get('total_in', 0)
        coins_out_total = coins_total.get('total_out', 0)
        coins_total_active = coins_total.get('total_active', 0)

        # user has commissions
        commission_amounts = user.account.commission_amounts

        self.context['IN'] = IN
        self.context['OUT'] = OUT
        self.context['SETTLEMENT'] = SETTLEMENT
        self.context['CAPTURE'] = CAPTURE
        self.context['EXPIRED'] = EXPIRED
        self.context['topups'] = topups[:5]
        self.context['coins'] = coins[:5]
        self.context['coins_in_total'] = coins_in_total if coins_in_total else 0
        self.context['coins_out_total'] = coins_out_total if coins_out_total else 0
        self.context['coins_total_active'] = coins_total_active if coins_total_active else 0
        self.context['commission_amounts'] = commission_amounts
        return render(request, self.template_name, self.context)
