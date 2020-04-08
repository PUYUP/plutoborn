from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Prefetch, Q, When, Value, IntegerField
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist

from utils.generals import get_model
from apps.payment.utils.constant import IN, OUT

Points = get_model('mypoints', 'Points')


class PointsListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/mypoints/points-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        points = Points.objects \
            .prefetch_related(Prefetch('user'), Prefetch('caused_content_type')) \
            .select_related('user', 'caused_content_type') \
            .filter(user_id=user.id)

        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        points_total = points.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out
        )
        points_in_total = points_total.get('total_in', 0)
        points_out_total = points_total.get('total_out', 0)
        points_total_active = points_total.get('total_active', 0)

        self.context['IN'] = IN
        self.context['OUT'] = OUT
        self.context['points'] = points
        self.context['points_in_total'] = points_in_total if points_in_total else 0
        self.context['points_out_total'] = points_out_total if points_out_total else 0
        self.context['points_total_active'] = points_total_active if points_total_active else 0
        self.context['coins_exchange'] = points_total_active / 1
        return render(request, self.template_name, self.context)
