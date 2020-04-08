from django.conf import settings

from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from utils.generals import get_model
from utils.midtransclient.error_midtrans import MidtransAPIError

from apps.payment.utils.general import money_to_coin
from apps.payment.utils.constant import SETTLEMENT, CAPTURE, EXPIRED

User = get_user_model()
SNAP = settings.SNAP


class TopUpListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'payment/topup-list.html'
    context = dict()

    def get(self, request):
        return render(request, self.template_name, self.context)


class TopUpDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'payment/topup-detail.html'
    context = dict()

    def get(self, request, topup_uuid=None):
        user = request.user
        try:
            topup = user.topups.get(uuid=topup_uuid)
        except ObjectDoesNotExist:
            return redirect(reverse('coin'))

        coin = money_to_coin(topup.payment_amount)

        if topup.payment_status != SETTLEMENT and topup.payment_status != CAPTURE and topup.payment_status != EXPIRED:
            try:
                payment_object = SNAP.transactions.status(topup.payment_order_id)
            except MidtransAPIError as e:
                payment_object = None

            if payment_object:
                payment_status = payment_object.get('transaction_status', None)
                payment_paid_date = payment_object.get('settlement_time', timezone.now())

                if payment_status == SETTLEMENT:
                    topup.payment_paid_date = payment_paid_date
                    topup.payment_status = SETTLEMENT

                if payment_status == 'expire' or payment_status == EXPIRED:
                    topup.payment_status = EXPIRED

                topup.save()
                topup.refresh_from_db()

        self.context['SETTLEMENT'] = SETTLEMENT
        self.context['CAPTURE'] = CAPTURE
        self.context['EXPIRED'] = EXPIRED
        self.context['topup'] = topup
        self.context['coin'] = coin
        return render(request, self.template_name, self.context)
