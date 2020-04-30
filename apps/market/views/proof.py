from django.views import View
from django.db.models import (
    Q, OuterRef, Subquery, Exists, Sum, Case, When, Value,
    IntegerField, F, Count
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from utils.generals import get_model
from apps.market.utils.constant import ACCEPT

Bundle = get_model('market', 'Bundle')
BoughtProofRequirement = get_model('market', 'BoughtProofRequirement')
BoughtProofDocument = get_model('market', 'BoughtProofDocument')


class BoughtProofView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/bought-proof.html'
    context = dict()

    def get(self, request, bundle_uuid=None):
        try:
            bundle = Bundle.objects.get(
                Q(uuid=bundle_uuid), Q(coin_amount__lte=0) | Q(coin_amount__isnull=True))
        except ObjectDoesNotExist:
            return redirect(reverse('bundle_list'))

        user = request.user
        bought = bundle.boughts.filter(user_id=user.id).first()

        if not bought:
            return redirect(reverse('bundle_list'))

        proof_document = BoughtProofDocument.objects \
            .filter(bought_proof_requirement_id=OuterRef('id'), user_id=user.id)

        proof_requirements = BoughtProofRequirement.objects \
            .filter(is_active=True) \
            .annotate(
                document_uuid=Subquery(proof_document.values('uuid')[:1]),
                document_image=Subquery(proof_document.values('value_image')[:1])
            )

        document_count = proof_requirements \
            .annotate(
                is_exist=Exists(proof_document.values('uuid'))
            ) \
            .aggregate(
                total=Count(Value(1), filter=F('is_exist'), output_field=IntegerField())
            )

        self.context['ACCEPT'] = ACCEPT
        self.context['bundle'] = bundle
        self.context['bought'] = bought
        self.context['proof_requirements'] = proof_requirements
        self.context['document_count'] = document_count['total']
        return render(request, self.template_name, self.context)
