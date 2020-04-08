from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, F, DateTimeField, CharField)
from django.core.exceptions import ObjectDoesNotExist

from utils.generals import get_model
from apps.market.utils.constant import PUBLISHED, GENERAL, NATIONAL

Bundle = get_model('market', 'Bundle')


class BundleListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/market/bundle-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        coin_amounts = user.account.coin_amounts

        packets = user.acquireds \
            .prefetch_related(Prefetch('packet'), Prefetch('user')) \
            .select_related('packet', 'user') \
            .annotate(
                question_total=Count('packet__questions', distinct=True),
                theory_total=Count('packet__questions__theory', distinct=True),
                x_start_date=Case(
                    When(packet__bundle__start_date__isnull=False, then=F('packet__bundle__start_date')),
                    default=F('packet__start_date'),
                    ouput_field=DateTimeField()
                ),
                x_end_date=Case(
                    When(packet__bundle__end_date__isnull=False, then=F('packet__bundle__end_date')),
                    default=F('packet__end_date'),
                    ouput_field=DateTimeField()
                ),
                x_simulation_type=Case(
                    When(packet__bundle__simulation_type=NATIONAL, then=Value('Nasional')),
                    default=Value('Umum'),
                    output_field=CharField()
                )
            )

        bundles = Bundle.objects \
            .annotate(total_packet=Count('packet', distinct=True)) \
            .filter(status=PUBLISHED) \
            .exclude(boughts__user_id=user.id)

        self.context['packets'] = packets
        self.context['bundles'] = bundles
        self.context['coin_amounts'] = coin_amounts
        return render(request, self.template_name, self.context)


class BundleDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/market/bundle-detail.html'
    context = dict()

    def get(self, request, bundle_uuid=None):
        user = request.user
        coin_amounts = user.account.coin_amounts

        try:
            bundle = Bundle.objects \
                .annotate(
                    total_packet=Count('packet', distinct=True),
                    is_boughted=Case(
                        When(boughts__user_id=user.id, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )) \
                .get(status=PUBLISHED, uuid=bundle_uuid)
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packets = bundle.packet \
            .prefetch_related(Prefetch('questions')) \
            .annotate(question_total=Count('questions', distinct=True))

        self.context['bundle'] = bundle
        self.context['packets'] = packets
        self.context['coin_amounts'] = coin_amounts
        return render(request, self.template_name, self.context)
