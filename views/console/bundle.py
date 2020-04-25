from django.conf import settings
from django.views import View
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
from apps.market.utils.constant import HOLD, ACCEPT
from views.console.forms import BundleForm

Bundle = get_model('market', 'Bundle')
Bought = get_model('market', 'Bought')


class BundleView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/bundle/list.html'
    context = dict()

    def get(self, request):
        bundles = Bundle.objects \
            .prefetch_related(Prefetch('packet')) \
            .all()

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
        return render(request, self.template_name, self.context)


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

        form = self.form(request.POST)
        if queryset:
            form = self.form(request.POST, instance=queryset)

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
        boughts = Bought.objects \
            .prefetch_related(Prefetch('user'), Prefetch('bundle')) \
            .select_related('user', 'bundle') \
            .all()

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(boughts, settings.PAGINATION_PER_PAGE)

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
        return render(request, self.template_name, self.context)


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
