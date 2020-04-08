from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef, CharField, Sum, FloatField, Max)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from utils.generals import get_model

Simulation = get_model('tryout', 'Simulation')
Packet = get_model('tryout', 'Packet')
Theory = get_model('tryout', 'Theory')
Answer = get_model('tryout', 'Answer')
User = get_model('auth', 'User')


class HomeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/home.html'
    context = dict()

    def get(self, request):
        user = request.user

        # redirect to admin dashboard
        if user.is_staff:
            return redirect(reverse('dashboard'))

        packets = Packet.objects.filter(simulations__user_id=user.id).distinct()
        ranking_chance = request.session.get('ranking_chance', 1)
        ranking_theory = request.session.get('ranking_theory', 0)
        ranking_packet = request.session.get('ranking_packet', 0)

        # make sure as integer
        if ranking_chance:
            ranking_chance = int(ranking_chance)

        if ranking_theory:
            ranking_theory = int(ranking_theory)

        if ranking_packet:
            ranking_packet = int(ranking_packet)

        try:
            packet = Packet.objects.get(id=ranking_packet)
        except ObjectDoesNotExist:
            packet = None

        if packet:
            simulation_count = user.simulations.filter(packet_id=packet.id).count()
            theories = packet.questions.filter(theory__isnull=False) \
                .distinct().values('theory_id', 'theory__label')

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
            if ranking_theory and ranking_theory > 0:
                answer_scores = answer_scores.filter(question__theory__id=ranking_theory)

            simulation = packet.simulations.filter(user_id=user.id, chance=ranking_chance).get()
            theory_stats = simulation.packet.questions.all() \
                .values('theory', 'theory__label') \
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
                    score_total=F('score_true_answer') - F('score_false_answer') + F('score_none_answer'),
                    score_average=F('score_total') / F('total_question')
                )

            theory_stats_higher = simulation.packet.questions.all() \
                .values('theory', 'theory_id', 'theory__label') \
                .annotate(theory_count=Count('theory', distinct=True)) \
                .values('answers__user') \
                .annotate(
                    total_true_answer=Count(
                        'theory__questions__answers', distinct=True, output_field=IntegerField(),
                        filter=Q(theory__questions__answers__isnull=False)
                        & Q(theory__questions__answers__user_id=F('answers__user'))
                        & Q(theory__questions__answers__simulation__user_id=F('answers__user'))
                        & Q(theory__questions__answers__choice__isnull=False)
                        & Q(theory__questions__answers__choice__right_choice=True)
                    ),
                    total_false_answer=Count(
                        'theory__questions__answers', distinct=True, output_field=IntegerField(),
                        filter=Q(theory__questions__answers__isnull=False)
                        & Q(theory__questions__answers__user_id=F('answers__user'))
                        & Q(theory__questions__answers__simulation__user_id=F('answers__user'))
                        & Q(theory__questions__answers__choice__isnull=False)
                        & Q(theory__questions__answers__choice__right_choice=False)
                    ),
                    total_none_answer=Count(
                        'theory__questions__answers', distinct=True, output_field=IntegerField(),
                        filter=Q(theory__questions__answers__isnull=False)
                        & Q(theory__questions__answers__user_id=F('answers__user'))
                        & Q(theory__questions__answers__simulation__user_id=F('answers__user'))
                        & Q(theory__questions__answers__choice__isnull=True)
                    ),
                    score_true_answer=F('total_true_answer') * F('theory__true_score'),
                    score_false_answer=F('total_false_answer') * F('theory__false_score'),
                    score_none_answer=F('total_none_answer') * F('theory__none_score'),
                    score_total=F('score_true_answer') - F('score_false_answer') + F('score_none_answer'),
                ) \
                .order_by('-score_total')
    
            page = request.GET.get('page', 1)
            paginate = Paginator(answer_scores, 10)
            answer_scores = paginate.get_page(page)

            self.context['simulation_count'] = simulation_count
            self.context['packet'] = packet
            self.context['answer_scores'] = answer_scores
            self.context['theories'] = theories
            self.context['theory_stats'] = theory_stats
            self.context['theory_stats_higher'] = theory_stats_higher

        self.context['packets'] = packets
        self.context['ranking_chance'] = ranking_chance
        self.context['ranking_theory'] = ranking_theory
        self.context['ranking_packet'] = ranking_packet
        return render(request, self.template_name, self.context)

    def post(self, request, simulation_uuid=None):
        chance = request.POST.get('chance', 1)
        theory = request.POST.get('theory', None)
        packet = request.POST.get('packet', None)

        # save temporary filter
        request.session['ranking_chance'] = chance
        request.session['ranking_theory'] = theory
        request.session['ranking_packet'] = packet
        return redirect(reverse('home'))
