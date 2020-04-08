from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef, CharField, Sum, FloatField, Max)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User

from utils.generals import get_model
from apps.payment.utils.constant import SETTLEMENT, CAPTURE

Packet = get_model('tryout', 'Packet')
Theory = get_model('tryout', 'Theory')
Answer = get_model('tryout', 'Answer')
TopUp = get_model('payment', 'TopUp')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/dashboard.html'
    context = dict()

    def get(self, request):
        topups = TopUp.objects \
            .filter(Q(payment_status=SETTLEMENT) | Q(payment_status=CAPTURE)) \
            .aggregate(total_amount=Sum('payment_amount'))

        self.context['total_user'] = User.objects.all().count()
        self.context['total_topup'] = topups['total_amount']
        self.context['total_affiliate'] = User.objects.filter(affiliate__isnull=False).count()
        return render(request, self.template_name, self.context)
