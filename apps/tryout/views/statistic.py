from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Q, Count, Case, When, Value, IntegerField, ExpressionWrapper

from utils.generals import get_model

Category = get_model('tryout', 'Category')
Simulation = get_model('tryout', 'Simulation')


class StatisticView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'tryout/statistic.html'
    context = dict()

    def get(self, request):
        category = int(request.session.get('category', 0))
        user = request.user

        simulations = Simulation.objects \
            .filter(user_id=user.id, acquired__packet__category_id=category, chance=1) \
            .annotate(
                tfn_total_question=Count('acquired__packet__questions',
                        filter=Q(acquired__packet__questions__theory__scoring_type='true_false_none')),
                preference_total_question=Count('acquired__packet__questions',
                        filter=Q(acquired__packet__questions__theory__scoring_type='preference')),
                
                tfn_true_score=Case(
                    When(
                        acquired__packet__questions__theory__scoring_type='true_false_none',
                        then=F('acquired__packet__questions__theory__true_score')
                    )
                ),
                tfn_false_score=Case(
                    When(
                        acquired__packet__questions__theory__scoring_type='true_false_none',
                        then=F('acquired__packet__questions__theory__false_score')
                    )
                ),
                tfn_none_score=Case(
                    When(
                        acquired__packet__questions__theory__scoring_type='true_false_none',
                        then=F('acquired__packet__questions__theory__none_score')
                    )
                ),

                tfn_total_true=Count(
                    F('acquired__packet__questions__answers'),
                    filter=Q(acquired__packet__questions__theory__scoring_type='true_false_none')
                    & Q(acquired__packet__questions__answers__right_choice=True),
                    output_field=IntegerField()
                ) * F('tfn_true_score'),

                tfn_total_false=Count(
                    F('acquired__packet__questions__answers'),
                    filter=Q(acquired__packet__questions__theory__scoring_type='true_false_none')
                    & Q(acquired__packet__questions__answers__right_choice=False),
                    output_field=IntegerField()
                ) * F('tfn_false_score'),

                tfn_total_none=Count(
                    F('acquired__packet__questions__answers'),
                    filter=Q(acquired__packet__questions__theory__scoring_type='true_false_none')
                    & Q(acquired__packet__questions__answers__isnull=True),
                    output_field=IntegerField()
                ) * F('tfn_none_score'),

                preference_total_score=Sum(
                    Case(
                        When(
                            acquired__packet__questions__theory__scoring_type='preference',
                            then=F('acquired__packet__questions__answers__choice__score')
                        ),
                        default=Value(0),
                        output_field=IntegerField()
                    ),
                    output_field=IntegerField()
                ),

                total_score=ExpressionWrapper(
                    F('preference_total_score') + F('tfn_total_true') + F('tfn_total_none') - F('tfn_total_false'),
                    output_field=IntegerField()
                )
            )

        simulations_highest = simulations.order_by('-total_score').first();

        self.context['category'] = category
        self.context['categories'] = Category.objects.all()
        self.context['simulations'] = simulations
        self.context['simulations_highest'] = simulations_highest
        return render(request, self.template_name, self.context)

    def post(self, request):
        category = request.POST.get('category', 0)

        # save temporary filter
        request.session['category'] = category
        return redirect(reverse('statistic'))
