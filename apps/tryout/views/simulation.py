from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef, CharField, Sum, FloatField)
from django.db.models.functions import Cast
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils import timezone

from utils.generals import get_model
from apps.tryout.utils.constant import SCORE, PREFERENCE, TRUE_FALSE_NONE

Packet = get_model('tryout', 'Packet')
Simulation = get_model('tryout', 'Simulation')
Answer = get_model('tryout', 'Answer')
Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')


class SimulationExamView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/tryout/simulation-exam.html'
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
            countdown = simulation.start_date + timezone.timedelta(minutes=simulation.duration_half)

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

    template_name = 'templates/tryout/simulation-result.html'
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

    template_name = 'templates/tryout/simulation-ranking.html'
    context = dict()

    def get(self, request, simulation_uuid=None):
        user = request.user

        try:
            simulation = Simulation.objects.get(uuid=simulation_uuid, user_id=user.id)
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        packet = simulation.packet
        simulation_count = user.simulations.filter(packet_id=packet.id).count()
        ranking_chance = int(request.session.get('ranking_chance', 1))
        ranking_theory = int(request.session.get('ranking_theory', 0))

        theories = packet.questions.filter(theory__isnull=False) \
            .values('theory', 'theory__pk', 'theory__label') \
            .annotate(total=Count('theory'))

        answer_scores = Answer.objects \
            .prefetch_related(Prefetch('user'), Prefetch('packet'), Prefetch('simulation'), Prefetch('question')) \
            .select_related('user', 'packet', 'simulation', 'qustion') \
            .filter(packet_id=packet.id, simulation__chance=ranking_chance) \
            .values('user') \
            .annotate(
                current_score=Case(
                    When(user_id=user.id, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
                total_true_answer=Sum(
                    Case(
                        When(Q(choice__isnull=False) & Q(right_choice=True), then=Value(1)),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                total_false_answer=Sum(
                    Case(
                        When(Q(choice__isnull=False) & Q(right_choice=False), then=Value(1)),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                total_none_answer=Sum(
                    Case(
                        When(choice__isnull=True, then=Value(1)),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                true_answer_score=Sum(
                    Case(
                        When(Q(choice__isnull=False) & Q(right_choice=True), then=F('question__theory__true_score')),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                false_answer_score=Sum(
                    Case(
                        When(Q(choice__isnull=False) & Q(right_choice=False), then=F('question__theory__false_score')),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                none_answer_score=Sum(
                    Case(
                        When(choice__isnull=True, then=F('question__theory__none_score')),
                        output_field=IntegerField(),
                        default=Value(0)
                    )
                ),
                total_score=F('true_answer_score') + F('none_answer_score') - F('false_answer_score')) \
            .values('user', 'user__username', 'current_score', 'true_answer_score', 'false_answer_score', 'none_answer_score', 'total_score', 'total_true_answer', 'total_false_answer', 'total_none_answer') \
            .order_by('-total_score')

        # theory filter
        if ranking_theory > 0:
            answer_scores = answer_scores.filter(question__theory__id=ranking_theory)

        # paginator
        page = request.GET.get('page', 1)
        paginate = Paginator(answer_scores, 10)
        answer_scores = paginate.get_page(page)

        self.context['simulation'] = simulation
        self.context['simulation_count'] = simulation_count
        self.context['packet'] = packet
        self.context['answer_scores'] = answer_scores
        self.context['ranking_chance'] = ranking_chance
        self.context['ranking_theory'] = ranking_theory
        self.context['theories'] = theories
        return render(request, self.template_name, self.context)

    def post(self, request, simulation_uuid=None):
        chance = request.POST.get('chance', 1)
        theory = request.POST.get('theory', 1)

        # save temporary filter
        request.session['ranking_chance'] = chance
        request.session['ranking_theory'] = theory
        return redirect(reverse('simulation_ranking', kwargs={'simulation_uuid': simulation_uuid}))
