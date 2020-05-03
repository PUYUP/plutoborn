from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef, CharField, Sum, FloatField)
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from utils.generals import get_model
from utils.pagination import Pagination
from apps.tryout.utils.constant import SCORE, PREFERENCE, TRUE_FALSE_NONE

from pprint import pprint

Packet = get_model('tryout', 'Packet')
Simulation = get_model('tryout', 'Simulation')
Answer = get_model('tryout', 'Answer')
Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')
Theory = get_model('tryout', 'Theory')


class SimulationExamView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'tryout/simulation-exam.html'
    context = dict()

    def get(self, request, simulation_uuid=None):
        user = request.user
        simulation = None
        countdown = None

        try:
            simulation = Simulation.objects.get(uuid=simulation_uuid, user_id=user.id)
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packet = simulation.packet
        answer_subquery = Answer.objects.filter(user_id=user.id, simulation__id=simulation.id)

        questions = packet.questions \
            .annotate(
                answer_id=Subquery(answer_subquery.filter(question__id=OuterRef('id')).values('id')[:1]),
                choice_id=Subquery(answer_subquery.filter(question__id=OuterRef('id'), choice__isnull=False).values('id')[:1])
            ).distinct().order_by('numbering')

        # ops! simulation is done, so redirect to simulation detail page
        if simulation.is_done:
            return redirect(reverse('simulation_result', kwargs={'simulation_uuid': simulation.uuid}))

        # Prepare countdown
        if simulation.start_date:
            if simulation.duration_half:
                countdown = simulation.start_date + timezone.timedelta(minutes=simulation.duration_half)
            else:
                countdown = simulation.start_date

        # Set to done if countdown larger than time now
        if not simulation.is_done and countdown <= timezone.now():
            simulation.is_done = True
            simulation.save()
            simulation.refresh_from_db()

        question = questions.first()
        choices = question.choices \
            .annotate(
                answer_id=Subquery(answer_subquery.filter(choice__id=OuterRef('id')).values('id')[:1])
            ).distinct().order_by('identifier')

        try:
            next_question = questions.filter(numbering__gt=question.numbering).first()
        except ObjectDoesNotExist:
            next_question = None

        try:
            prev_question = questions.filter(numbering__lt=question.numbering).first()
        except ObjectDoesNotExist:
            prev_question = None

        self.context['SCORE'] = SCORE
        self.context['packet'] = packet
        self.context['question'] = question
        self.context['questions'] = questions
        self.context['choices'] = choices
        self.context['countdown'] = countdown
        self.context['simulation'] = simulation
        self.context['next_question'] = next_question
        self.context['prev_question'] = prev_question
        return render(request, self.template_name, self.context)


class SimulationResultView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'tryout/simulation-result.html'
    context = dict()

    def get(self, request, simulation_uuid=None):
        user = request.user

        try:
            simulation = Simulation.objects.get(uuid=simulation_uuid, user_id=user.id)
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packet = simulation.packet
        answer_subquery = Answer.objects.filter(user_id=user.id, simulation__id=simulation.id)
        questions = packet.questions \
            .annotate(
                answer_id=Subquery(
                    answer_subquery.filter(question__id=OuterRef('id')).values('id')[:1]
                ),
                choice_id=Subquery(
                    answer_subquery.filter(question__id=OuterRef('id'), choice__isnull=False).values('id')[:1]
                ),
                choice_identifier=Subquery(
                    answer_subquery.filter(
                        question__id=OuterRef('id'), choice__isnull=False).values('choice__identifier')[:1]
                )
            ).distinct().order_by('numbering')

        question = questions.first()
        choices = question.choices \
            .annotate(
                answer_id=Subquery(answer_subquery.filter(choice__id=OuterRef('id')).values('id')[:1])
            ).order_by('identifier')

        try:
            next_question = questions.filter(numbering__gt=question.numbering).first()
        except ObjectDoesNotExist:
            next_question = None

        try:
            prev_question = questions.filter(numbering__lt=question.numbering).first()
        except ObjectDoesNotExist:
            prev_question = None

        try:
            answer = answer_subquery.get(id=question.answer_id)
        except ObjectDoesNotExist:
            answer = None

        try:
            choice = choices.get(right_choice=True)
        except ObjectDoesNotExist:
            choice = None

        # STATS LOGIC!
        simulation_stats = packet.questions.filter(theory__isnull=False, theory__scoring_type=TRUE_FALSE_NONE) \
            .values('theory', 'theory_id', 'theory__label') \
            .annotate(
                total_question=Count(
                    'theory__questions', distinct=True, output_field=IntegerField(),
                    filter=Q(theory__questions__packet__id=simulation.packet.id)
                ),
                total_has_answer=Count(
                    'theory__questions__answers', distinct=True, output_field=IntegerField(),
                    filter=Q(theory__questions__answers__isnull=False)
                    & Q(theory__questions__answers__user_id=user.id)
                    & Q(theory__questions__answers__simulation_id=simulation.id)
                ),
                total_not_answer=F('total_question') - F('total_has_answer'),
                total_true_answer=Count(
                    'theory__questions__answers', distinct=True, output_field=IntegerField(),
                    filter=Q(theory__questions__answers__isnull=False)
                    & Q(theory__questions__answers__user_id=user.id)
                    & Q(theory__questions__answers__simulation_id=simulation.id)
                    & Q(theory__questions__answers__choice__isnull=False)
                    & Q(theory__questions__answers__choice__right_choice=True)
                ),
                total_false_answer=Count(
                    'theory__questions__answers', distinct=True, output_field=IntegerField(),
                    filter=Q(theory__questions__answers__isnull=False)
                    & Q(theory__questions__answers__user_id=user.id)
                    & Q(theory__questions__answers__simulation_id=simulation.id)
                    & Q(theory__questions__answers__choice__isnull=False)
                    & Q(theory__questions__answers__choice__right_choice=False)
                ),
                total_none_answer=Count(
                    'theory__questions__answers', distinct=True, output_field=IntegerField(),
                    filter=Q(theory__questions__answers__isnull=False)
                    & Q(theory__questions__answers__user_id=user.id)
                    & Q(theory__questions__answers__simulation_id=simulation.id)
                    & Q(theory__questions__answers__choice__isnull=True)
                ),
                score_true_answer=F('total_true_answer') * F('theory__true_score'),
                score_false_answer=F('total_false_answer') * F('theory__false_score'),
                score_none_answer=F('total_none_answer') * F('theory__none_score'),
                score_total=F('score_true_answer') + F('score_false_answer') + F('score_none_answer'),
                score_average=F('score_total') / F('total_question')
            )

        spaces = Choice.objects \
            .filter(
                packet__questions__choices__question_id=OuterRef('id'),
                question__theory__scoring_type=PREFERENCE
            ).order_by().values('packet__questions__choices__question_id')
        count_spaces = spaces.annotate(c=Count('id', distinct=True)).values('c')

        simulation_stats_preference = packet.questions.filter(theory__isnull=False, theory__scoring_type=PREFERENCE) \
            .values('theory', 'theory_id', 'theory__label') \
            .annotate(
                total_choice=Subquery(count_spaces),
                total_question=Count(
                    'id', distinct=True, output_field=IntegerField(),
                    filter=Q(packet__id=simulation.packet.id)
                ),
                total_has_answer=Count(
                    'answers__id', distinct=True, output_field=IntegerField(),
                    filter=Q(answers__isnull=False)
                    & Q(answers__user_id=user.id)
                    & Q(answers__simulation_id=simulation.id)
                    & Q(answers__packet_id=simulation.packet.id)
                ),
                total_not_answer=F('total_question') - F('total_has_answer'),
                total_score=Sum(
                    'answers__choice__score', output_field=IntegerField(),
                    filter=Q(answers__user_id=user.id)
                    & Q(answers__simulation_id=simulation.id)
                    & Q(answers__packet_id=simulation.packet.id)
                )
            )

        self.context['SCORE'] = SCORE
        self.context['packet'] = packet
        self.context['question'] = question
        self.context['answer'] = answer
        self.context['simulation_stats'] = simulation_stats
        self.context['simulation_stats_preference'] = simulation_stats_preference
        self.context['questions'] = questions
        self.context['choices'] = choices
        self.context['choice'] = choice
        self.context['simulation'] = simulation
        self.context['next_question'] = next_question
        self.context['prev_question'] = prev_question
        return render(request, self.template_name, self.context)


class SimulationRankingView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'tryout/simulation-ranking.html'
    context = dict()

    def get(self, request, simulation_uuid=None):
        user = request.user

        try:
            simulation = Simulation.objects.get(uuid=simulation_uuid, user_id=user.id)
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packet = simulation.packet
        simulation_count = user.simulations.filter(packet_id=packet.id).count()
        simulation_change = int(request.session.get('simulation_change', 1))
        ranking_theory = int(request.session.get('ranking_theory', 0))

        theories = packet.questions.filter(theory__isnull=False) \
            .annotate(question_count=Count('theory__questions', distinct=True)) \
            .values('theory', 'theory__pk', 'theory__label', 'theory__true_score',
                    'theory__false_score', 'theory__none_score', 'theory__scoring_type',
                    'question_count') \
            .distinct()

        theories_params = dict()
        theories_total_score = list()
        theories_filtered = theories

        if ranking_theory:
            theories_filtered = theories.filter(theory__id=ranking_theory)

        to = Theory.objects.filter(questions__packet_id=OuterRef('packet_id')) \
            .annotate(
                question_total=Count(
                    'questions', distinct=True,
                    output_field=IntegerField()
                )
            )

        for item in theories_filtered:
            theory_id = item['theory__pk']
            scoring_type = item['theory__scoring_type']
            question_count = item['question_count']

            at = 'theory_{}_true_count'.format(theory_id)
            af = 'theory_{}_false_count'.format(theory_id)
            an = 'theory_{}_none_count'.format(theory_id)

            at_s = 'theory_{}_true_score'.format(theory_id)
            af_s = 'theory_{}_false_score'.format(theory_id)
            an_s = 'theory_{}_none_score'.format(theory_id)

            ts = 'theory_{}_total_score'.format(theory_id)
            tn = 'theory_{}_verbose_name'.format(theory_id)
            st = 'theory_{}_scoring_type'.format(theory_id)

            qt = 'theory_{}_question_total'.format(theory_id)
            pt_s = 'theory_{}_preference_score_total'.format(theory_id)

            # verbose name
            theories_params[tn] = Value(item['theory__label'], output_field=CharField())
            theories_params[st] = Value(scoring_type, output_field=CharField())

            # count questions
            theories_params[qt] = Subquery(to.filter(id=theory_id).values('question_total')[:1])

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

            if scoring_type == TRUE_FALSE_NONE:
                # sum all theory score
                theories_params[ts] = (F(at) * item['theory__true_score']) \
                    + (F(an) * item['theory__none_score']) \
                    - (F(af) * item['theory__false_score'])

            elif scoring_type == PREFERENCE:
                theories_params[ts] = F(pt_s)

            # prepare total score
            theories_total_score.append(F(ts))

        simulations = packet.simulations \
            .filter(chance=simulation_change) \
            .annotate(
                **theories_params,
                total_score=sum(theories_total_score),
                current_score=Case(
                    When(user_id=user.id, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
            ) \
            .order_by('-total_score')

        theory_ids = [item['theory__pk'] for item in theories_filtered]
        for item in simulations:
            tgs = list()
            for tid in theory_ids:
                st = 'theory_{}_scoring_type'.format(tid)
                tn = 'theory_{}_verbose_name'.format(tid)
                ts = 'theory_{}_total_score'.format(tid)
                at_s = 'theory_{}_true_score'.format(tid)
                af_s = 'theory_{}_false_score'.format(tid)
                an_s = 'theory_{}_none_score'.format(tid)
                pt_s = 'theory_{}_preference_score_total'.format(tid)

                label = getattr(item, tn, None)
                true_score = getattr(item, at_s, 0)
                false_score = getattr(item, af_s, 0)
                none_score = getattr(item, an_s, 0)
                total_score = getattr(item, ts, 0)
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
            item.theory_groups = tgs

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(simulations, settings.PAGINATION_PER_PAGE)

        try:
            simulations_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            simulations_pagination = paginator.page(1)
        except EmptyPage:
            simulations_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, simulations, simulations_pagination, page_num, paginator)

        self.context['TRUE_FALSE_NONE'] = TRUE_FALSE_NONE
        self.context['PREFERENCE'] = PREFERENCE
        self.context['pagination'] = pagination
        self.context['simulation'] = simulation
        self.context['simulations'] = simulations
        self.context['simulations_pagination'] = simulations_pagination
        self.context['simulation_count'] = simulation_count
        self.context['packet'] = packet
        self.context['simulation_change'] = simulation_change
        self.context['ranking_theory'] = ranking_theory
        self.context['theories'] = theories
        self.context['theories_filtered'] = theories_filtered
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, simulation_uuid=None):
        chance = request.POST.get('chance', 1)
        theory = request.POST.get('theory', 1)

        # save temporary filter
        request.session['simulation_change'] = chance
        request.session['ranking_theory'] = theory
        return redirect(reverse('simulation_ranking', kwargs={'simulation_uuid': simulation_uuid}))


class RankingListView(View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'tryout/simulation-ranking-list.html'
    context = dict()

    def get(self, request):
        user = request.user

        simulation = Simulation.objects \
            .filter(acquired_id=OuterRef('id'), chance=1) \
            .order_by('chance')

        acquireds = user.acquireds \
            .annotate(
                simulation_uuid=Subquery(simulation.values('uuid')[:1])
            ) \
            .filter(simulations__isnull=False)

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(acquireds, settings.PAGINATION_PER_PAGE)

        try:
            acquireds_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            acquireds_pagination = paginator.page(1)
        except EmptyPage:
            acquireds_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, acquireds, acquireds_pagination, page_num, paginator)

        self.context['acquireds'] = acquireds
        self.context['acquireds_pagination'] = acquireds_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
