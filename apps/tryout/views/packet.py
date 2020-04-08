from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef)
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from utils.generals import get_model
from apps.tryout.utils.constant import SCORE
from apps.market.utils.constant import NATIONAL
from apps.tryout.forms import PasswordProtectForm

Packet = get_model('tryout', 'Packet')
Simulation = get_model('tryout', 'Simulation')
Answer = get_model('tryout', 'Answer')
BundlePasswordPassed = get_model('market', 'BundlePasswordPassed')
ProgramStudy = get_model('tryout', 'ProgramStudy')


class PacketDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'templates/tryout/packet-detail.html'
    context = dict()
    form = PasswordProtectForm

    def get_packet(self, packet_uuid=None, user=None):
        try:
            packet = Packet.objects \
                .prefetch_related(Prefetch('questions')) \
                .annotate(
                    chance_total=Count('simulations', distinct=True, filter=Q(simulations__user_id=user.id)),
                    question_total=Count('questions', distinct=True),
                    theory_total=Count('questions__theory', distinct=True),
                    acquired_id=F('acquireds__id'),
                    in_simulate=Case(
                        When(Q(simulations__isnull=False) & Q(simulations__user_id=user.id), then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                ) \
                .get(uuid=packet_uuid, acquireds__user_id=user.id)

            return packet
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

    def get(self, request, packet_uuid=None):
        user = request.user
        packet = self.get_packet(packet_uuid=packet_uuid, user=user)
        simulations = packet.simulations.filter(user_id=request.user.id).order_by('-date_created')
        bundle = packet.bundle_set.first()
        bundle_password = packet.bundle_set.filter(password__isnull=False, bundle_passwords__isnull=False)

        self.context['SCORE'] = SCORE
        self.context['NATIONAL'] = NATIONAL
        self.context['packet'] = packet
        self.context['bundle'] = bundle
        self.context['simulations'] = simulations
        self.context['form'] = self.form(bundle=bundle, request=request)
        self.context['bundle_password'] = bundle_password.exists()
        self.context['program_studies'] = ProgramStudy.objects.all()
        return render(request, self.template_name, self.context)

    def post(self, request, packet_uuid=None):
        user = request.user
        packet = self.get_packet(packet_uuid=packet_uuid, user=user)
        bundle = packet.bundle_set.first()

        form = self.form(request.POST, bundle=bundle, request=request)
        if form.is_valid():
            password = form.cleaned_data.get('password', None)

            # save password
            BundlePasswordPassed.objects.create(user=user, bundle=bundle, password=password)
            return redirect(reverse('packet_detail', kwargs={'packet_uuid': packet_uuid}))

        self.context['form'] = form
        return render(request, self.template_name, self.context)
