from django.conf import settings
from django.views import View
from django.db import transaction
from django.db.models import Prefetch, OuterRef, Subquery
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

# Google Drive
from gdstorage.storage import GoogleDriveStorage

from utils.generals import get_model
from utils.pagination import Pagination
from apps.market.utils.constant import HOLD, ACCEPT
from views.console.forms import BundleForm

Bundle = get_model('market', 'Bundle')
Bought = get_model('market', 'Bought')
BoughtProofRequirement = get_model('market', 'BoughtProofRequirement')
BoughtProof = get_model('market', 'BoughtProof')
BoughtProofDocument = get_model('market', 'BoughtProofDocument')
gd_storage = GoogleDriveStorage()


class BundleView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/bundle/list.html'
    context = dict()

    def get(self, request):
        bundles = Bundle.objects \
            .prefetch_related(Prefetch('packet')) \
            .all()

        coin_amount = str(request.session.get('coin_amount', ''))
        if coin_amount is not None:
            if coin_amount == '0':
                bundles = bundles.filter(coin_amount=0)

            if coin_amount > '0':
                bundles = bundles.filter(coin_amount__gt=0)

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(bundles, settings.PAGINATION_PER_PAGE)

        try:
            bundles_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            bundles_pagination = paginator.page(1)
        except EmptyPage:
            bundles_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, bundles, bundles_pagination, page_num, paginator)

        self.context['bundles'] = bundles
        self.context['bundles_pagination'] = bundles_pagination
        self.context['pagination'] = pagination
        self.context['coin_amount'] = coin_amount
        return render(request, self.template_name, self.context)  

    @transaction.atomic
    def post(self, request):
        coin_amount = request.POST.get('coin_amount', None)

        # save temporary filter
        request.session['coin_amount'] = coin_amount
        return redirect(reverse('dashboard_bundle'))


class BundleEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/bundle/editor.html'
    context = dict()
    form = BundleForm

    def get(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            form = self.form(request.POST, instance=queryset)
        else:
            form = self.form(request.POST)

        if form.is_valid():
            fm = form.save(commit=False)
            fm.save()
            form.save_m2m()

            if queryset:
                msg = _("Bundel %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Bundel %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_bundle'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class BundleDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Bundel %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_bundle'))


class BoughtView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/bundle/bought.html'
    context = dict()

    def get(self, request):
        proof_reqs= BoughtProofRequirement.objects.all()
        proof_reqs_id = proof_reqs.values_list('id', flat=True)
        xos = dict()

        for item in proof_reqs:
            d = Subquery(
                    BoughtProofDocument.objects \
                    .filter(
                        bought_proof__bought__id=OuterRef('id'),
                        bought_proof_requirement__id=item.id) \
                    .values('value_image')[:1]
            )

            xos.update(**{'doc_%s' % item.id: d})

        boughts = Bought.objects \
            .prefetch_related(Prefetch('user'), Prefetch('bundle')) \
            .select_related('user', 'bundle') \
            .annotate(**xos) \
            .all()

        for item in boughts:
            docs = list()
            for p in proof_reqs_id:
                doc = 'doc_%s' % p
                doc_file = getattr(item, doc, None)
                if doc_file:
                    file_data = gd_storage._check_file_exists(doc_file)
                    x = {
                        'view_url': file_data['webViewLink'] if file_data else '',
                        'thumb_url': file_data['thumbnailLink'] if file_data else '',
                    }
                    docs.append(x)
            item.proofs = docs 

        status = str(request.session.get('status', ''))
        if status is not None:
            if status == 'hold':
                boughts = boughts.filter(status='hold')

            if status == 'accept':
                boughts = boughts.filter(status='accept')

        # paginator
        item_per_page = int(request.session.get('item_per_page', settings.PAGINATION_PER_PAGE))
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(boughts, item_per_page)

        try:
            boughts_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            boughts_pagination = paginator.page(1)
        except EmptyPage:
            boughts_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, boughts, boughts_pagination, page_num, paginator)

        self.context['boughts'] = boughts
        self.context['boughts_pagination'] = boughts_pagination
        self.context['pagination'] = pagination
        self.context['status'] = status
        self.context['item_per_page'] = item_per_page
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request):
        if request.is_ajax():
            id = request.POST.get('id')
            status = True
    
            try:
                bought = Bought.objects.get(id=id)
            except ObjectDoesNotExist:
                status = False

            if not request.user.is_staff:
                status = False

            if status:
                bought.status = ACCEPT
                bought.save()

            return JsonResponse({'id': id, 'status': status})
        else:
            status = request.POST.get('status', None)
            item_per_page = request.POST.get('item-per-page', settings.PAGINATION_PER_PAGE)

            # save temporary filter
            request.session['status'] = status
            request.session['item_per_page'] = item_per_page
            return redirect(reverse('dashboard_bought'))


class BoughtDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/bundle/bought-detail.html'
    context = dict()

    def get(self, request, pk=None):
        try:
            bought = Bought.objects.get(id=pk)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_bought'))

        """
        proof_docs = bought.bought_proof.bought_proof_documents.all()
        for item in proof_docs:
            if item.value_image:
                fname = item.value_image.name
                file_data = gd_storage._check_file_exists(fname)
                x = {
                    'view_url': file_data['webViewLink'] if file_data else '',
                    'thumb_url': file_data['thumbnailLink'] if file_data else '',
                }
                item.proofs = x
        """

        self.context['HOLD'] = HOLD
        self.context['bought'] = bought
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)


class BoughtAcceptView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    context = dict()

    def get(self, request, pk=None):
        try:
            bought = Bought.objects.get(id=pk)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_bought'))

        if not request.user.is_staff:
            return redirect(reverse('home'))

        bought.status = ACCEPT
        bought.save()

        msg = _("Pembelian Bundel berhasil disetujui.")
        messages.add_message(request, messages.INFO, msg)

        return redirect(reverse('dashboard_bought_detail', kwargs={'pk': pk}))
