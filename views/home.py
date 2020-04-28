import datetime

from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef, CharField, Sum, FloatField, Max, DateTimeField)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from utils.generals import get_model
from apps.market.utils.constant import PUBLISHED, NATIONAL
from apps.tryout.utils.constant import PREFERENCE, TRUE_FALSE_NONE

Simulation = get_model('tryout', 'Simulation')
Bundle = get_model('market', 'Bundle')
CMSBanner = get_model('cms', 'CMSBanner')
CMSVideo = get_model('cms', 'CMSVideo')


class HomeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'home.html'
    context = dict()

    def latest_simulation(self):
        user = self.request.user
        try:
            latest_simulation = Simulation.objects.filter(user_id=user.id).latest('date_created')
        except ObjectDoesNotExist:
            latest_simulation = None

        if not latest_simulation:
            return None

        packet = latest_simulation.packet
        chance = latest_simulation.chance

        theories = packet.questions.filter(theory__isnull=False) \
            .values('theory', 'theory__pk', 'theory__label', 'theory__true_score',
                    'theory__false_score', 'theory__none_score', 'theory__scoring_type') \
            .distinct()

        theories_params = dict()
        theories_total_score = list()

        for item in theories:
            theory_id = item['theory__pk']
            scoring_type = item['theory__scoring_type']

            at = 'theory_{}_true_count'.format(theory_id)
            af = 'theory_{}_false_count'.format(theory_id)
            an = 'theory_{}_none_count'.format(theory_id)

            at_s = 'theory_{}_true_score'.format(theory_id)
            af_s = 'theory_{}_false_score'.format(theory_id)
            an_s = 'theory_{}_none_score'.format(theory_id)

            ts = 'theory_{}_total_score'.format(theory_id)
            tn = 'theory_{}_verbose_name'.format(theory_id)

            pt_s = 'theory_{}_preference_score_total'.format(theory_id)

            # verbose name
            theories_params[tn] = Value(item['theory__label'], output_field=CharField())

            # score by preference
            theories_params[pt_s] = Sum(
                Case(
                    When(
                        Q(answers__question__theory__id=theory_id)
                        & Q(answers__question__theory__scoring_type=PREFERENCE)
                        & Q(answers__choice__isnull=False),
                        then=F('answers__choice__score')
                    ),
                    output_field=IntegerField(),
                    default=Value(0)
                )
            )

            # count right choice
            theories_params[at] = Sum(
                Case(
                    When(
                        Q(answers__question__theory__id=theory_id)
                        & Q(answers__choice__isnull=False)
                        & Q(answers__choice__right_choice=True),
                        then=Value(1)
                    ),
                    output_field=IntegerField(),
                    default=Value(0)
                )
            )
            theories_params[at_s] = F(at) * item['theory__true_score']

            # count false choice
            theories_params[af] = Sum(
                Case(
                    When(
                        Q(answers__question__theory__id=theory_id)
                        & Q(answers__choice__isnull=False)
                        & Q(answers__choice__right_choice=False),
                        then=Value(1)
                    ),
                    output_field=IntegerField(),
                    default=Value(0)
                )
            )
            theories_params[af_s] = F(af) * item['theory__false_score']

            # count none choice
            theories_params[an] = Sum(
                Case(
                    When(
                        Q(answers__question__theory__id=theory_id)
                        & Q(answers__choice__isnull=True),
                        then=Value(1)
                    ),
                    output_field=IntegerField(),
                    default=Value(0)
                )
            )
            theories_params[an_s] = F(an) * item['theory__none_score']

            # sum all theory score
            if scoring_type == TRUE_FALSE_NONE:
                # sum all theory score
                theories_params[ts] = (F(at) * item['theory__true_score']) \
                    + (F(an) * item['theory__none_score']) \
                    - (F(af) * item['theory__false_score'])

            elif scoring_type == PREFERENCE:
                theories_params[ts] = F(pt_s)

            # prepare total score
            theories_total_score.append(F(ts))

        simulations = Simulation.objects.filter(packet_id=packet.id, chance=chance) \
            .annotate(
                **theories_params,
                total_score=sum(theories_total_score),
                current_score=Case(
                    When(user_id=user.id, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
            ).order_by('-total_score')

        theory_ids = [item['theory__pk'] for item in theories]
        simulation = simulations.filter(user_id=user.id).get()

        tgs = list()
        for tid in theory_ids:
            st = 'theory_{}_scoring_type'.format(tid)
            tn = 'theory_{}_verbose_name'.format(tid)
            ts = 'theory_{}_total_score'.format(tid)
            at_s = 'theory_{}_true_score'.format(tid)
            af_s = 'theory_{}_false_score'.format(tid)
            an_s = 'theory_{}_none_score'.format(tid)
            pt_s = 'theory_{}_preference_score_total'.format(tid)

            label = getattr(simulation, tn, None)
            true_score = getattr(simulation, at_s, 0)
            false_score = getattr(simulation, af_s, 0)
            none_score = getattr(simulation, an_s, 0)
            total_score = getattr(simulation, ts, 0)
            preference_total_score = getattr(item, pt_s, 0)
            scoring_type = getattr(item, st, None)

            tg = {
                'label': label,
                'true_score': true_score,
                'false_score': false_score,
                'none_score': none_score,
                'total_score': total_score,
                'preference_total_score': preference_total_score,
                'scoring_type': scoring_type,
            }
            tgs.append(tg)

        simulation.theory_groups = tgs
        rank = simulations.filter(total_score__gt=simulation.total_score).count() + 1
        return {'simulation': simulation, 'rank': rank}

    def get(self, request):
        user = request.user
        account = user.account

        # redirect to admin dashboard
        if user.is_staff:
            return redirect(reverse('dashboard'))

        if user.profile.is_empty:
            return redirect(reverse('profile'))

        simulation_stat = self.latest_simulation()
        settings.TIME_ZONE  # 'UTC'
        aware_datetime = timezone.make_aware(timezone.datetime.today())
        aware_datetime.tzinfo  # <UTC>
        simulation_due = Bundle.objects.filter(start_date__gt=aware_datetime).first()

        bundles = Bundle.objects \
            .annotate(total_packet=Count('packet', distinct=True)) \
            .filter(status=PUBLISHED) \
            .exclude(boughts__user_id=user.id)[:4]

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
            )[:4]
    
        # CMS
        banners = CMSBanner.objects.filter(is_active=True).order_by('sort')
        videos = CMSVideo.objects.filter(is_active=True).order_by('sort')

        self.context['simulation_due'] = simulation_due
        self.context['simulation_stat'] = simulation_stat
        self.context['my_coins'] = account.coin_amounts
        self.context['my_points'] = account.points_amounts
        self.context['bundles'] = bundles
        self.context['packets'] = packets

        # CMS
        self.context['banners'] = banners
        self.context['videos'] = videos
        return render(request, self.template_name, self.context)
