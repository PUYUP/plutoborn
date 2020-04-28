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
from views.console.cms.forms import CMSVideoForm, CMSBannerForm

CMSBanner = get_model('cms', 'CMSBanner')
CMSVideo = get_model('cms', 'CMSVideo')


class CMSView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/cms/index.html'
    context = dict()

    def get(self, request):
        return render(request, self.template_name, self.context)


class CMSBannerView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/cms/banner.html'
    context = dict()

    def get(self, request):
        queryset = CMSBanner.objects.all()

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(queryset, settings.PAGINATION_PER_PAGE)

        try:
            queryset_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            queryset_pagination = paginator.page(1)
        except EmptyPage:
            queryset_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, queryset, queryset_pagination, page_num, paginator)

        self.context['queryset'] = queryset
        self.context['queryset_pagination'] = queryset_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)


class CMSBannerEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/cms/banner-editor.html'
    context = dict()
    form = CMSBannerForm

    def get(self, request, pk=None):
        try:
            queryset = CMSBanner.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, pk=None):
        try:
            queryset = CMSBanner.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        form = self.form(request.POST, request.FILES)
        if queryset:
            form = self.form(request.POST, request.FILES, instance=queryset)

        if form.is_valid():
            fm = form.save(commit=False)
            fm.save()
            form.save_m2m()

            if queryset:
                msg = _("Banner %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Banner %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('cms_banner'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class CMSBannerDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = CMSBanner.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Banner %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('cms_banner'))


class CMSVideoView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/cms/video.html'
    context = dict()

    def get(self, request, pk=None):
        queryset = CMSVideo.objects.all()

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(queryset, settings.PAGINATION_PER_PAGE)

        try:
            queryset_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            queryset_pagination = paginator.page(1)
        except EmptyPage:
            queryset_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, queryset, queryset_pagination, page_num, paginator)

        self.context['queryset'] = queryset
        self.context['queryset_pagination'] = queryset_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)


class CMSVideoEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/cms/video-editor.html'
    context = dict()
    form = CMSVideoForm

    def get(self, request, pk=None):
        try:
            queryset = CMSVideo.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, pk=None):
        try:
            queryset = CMSVideo.objects.get(pk=pk)
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
                msg = _("Video %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Video %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('cms_video'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class CMSVideoDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = CMSVideo.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Video %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('cms_video'))
