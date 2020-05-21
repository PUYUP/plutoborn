from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, F, DateTimeField, CharField, Q)
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
from apps.market.utils.constant import PUBLISHED, GENERAL, NATIONAL, ACCEPT
from apps.tryout.utils.constant import ACTIVE, HOLD

Bundle = get_model('market', 'Bundle')
Question = get_model('tryout', 'Question')
ProgramStudy = get_model('tryout', 'ProgramStudy')


class BundleListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/bundle-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        coin_amounts = user.account.coin_amounts
        slug = None

        if 'enrolled' in request.path:
            slug = 'enrolled'

            queryset = user.acquireds \
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
                        When(packet__bundle__simulation_type=NATIONAL, then=Value(NATIONAL)),
                        default=Value(GENERAL),
                        output_field=CharField()
                    ),
                    x_simulation_type_label=Case(
                        When(packet__bundle__simulation_type=NATIONAL, then=Value('Nasional')),
                        default=Value('Umum'),
                        output_field=CharField()
                    ),
                    x_bundle_is_password=Case(
                        When(packet__bundle__password__isnull=False, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    ),
                    x_is_password_passed=Case(
                        When(
                            Q(packet__bundle__bundle_passwords__isnull=False) & Q(packet__bundle__bundle_passwords__user_id=user.id),
                            then=Value(True)
                        ),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                ).order_by('-date_created')
        else:
            queryset = Bundle.objects \
                .prefetch_related(Prefetch('packet')) \
                .annotate(total_packet=Count('packet', distinct=True)) \
                .filter(status=PUBLISHED) \
                .exclude(boughts__user_id=user.id) \
                .order_by('-date_created')

        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(queryset, settings.PAGINATION_PER_PAGE)

        try:
            queryset_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            queryset_pagination = paginator.page(1)
        except EmptyPage:
            queryset_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, queryset, queryset_pagination, page_num, paginator)

        self.context['ACTIVE'] = ACTIVE
        self.context['HOLD'] = HOLD
        self.context['GENERAL'] = GENERAL
        self.context['NATIONAL'] = NATIONAL
        self.context['slug'] = slug
        self.context['queryset'] = queryset
        self.context['queryset_pagination'] = queryset_pagination
        self.context['pagination'] = pagination
        self.context['coin_amounts'] = coin_amounts
        self.context['program_studies'] = ProgramStudy.objects.all()
        return render(request, self.template_name, self.context)


class BundleDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/bundle-detail.html'
    context = dict()

    def get(self, request, bundle_uuid=None):
        user = request.user
        coin_amounts = user.account.coin_amounts

        try:
            bundle = Bundle.objects \
                .filter(status=PUBLISHED, uuid=bundle_uuid) \
                .annotate(total_packet=Count('packet', distinct=True)) \
                .get()
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packets = bundle.packet \
            .prefetch_related(Prefetch('questions')) \
            .annotate(question_total=Count('questions', distinct=True))

        for x in packets:
            theory = x.questions.distinct() \
                .values('theory', 'theory__label', 'theory__duration') \
                .annotate(question_total=Count('theory__questions', distinct=True, filter=Q(theory__questions__packet_id=x.id)))
            x.theory = theory

        is_boughted = bundle.boughts.filter(user_id=user.id).exists()
        is_accept = bundle.boughts.filter(user_id=user.id, status=ACCEPT).exists()

        self.context['is_boughted'] = is_boughted
        self.context['is_accept'] = is_accept
        self.context['bundle'] = bundle
        self.context['packets'] = packets
        self.context['coin_amounts'] = coin_amounts
        return render(request, self.template_name, self.context)
