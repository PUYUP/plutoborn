from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, F, IntegerField, Sum, Q)
from django.db.models.functions import Coalesce
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.generals import get_model
from utils.pagination import Pagination
from apps.payment.utils.constant import IN, OUT

Affiliate = get_model('market', 'Affiliate')
AffiliateCapture = get_model('market', 'AffiliateCapture')
AffiliateAcquired = get_model('market', 'AffiliateAcquired')
AffiliateCommission = get_model('market', 'AffiliateCommission')


class AffiliateView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/affiliate.html'
    context = dict()

    def get(self, request):
        user = request.user
        affiliate =  getattr(user, 'affiliate', None)

        if not affiliate:
            affiliate = Affiliate.objects.create(user=user)
            affiliate.refresh_from_db()
        
        acquireds = AffiliateAcquired.objects.filter(affiliate_id=affiliate.id).order_by('-date_created')
        commissions = AffiliateCommission.objects \
            .prefetch_related(Prefetch('creator'), Prefetch('affiliator'), Prefetch('caused_content_type')) \
            .select_related('creator', 'affiliator', 'caused_content_type') \
            .filter(affiliator_id=user.id).order_by('-date_created')
    
        sum_in = Coalesce(Sum('amount', filter=Q(transaction_type=IN), output_field=IntegerField()), 0)
        sum_out = Coalesce(Sum('amount', filter=Q(transaction_type=OUT), output_field=IntegerField()), 0)

        commissions_total = commissions.aggregate(
            total_in=sum_in,
            total_out=sum_out,
            total_active=sum_in - sum_out
        )
        commissions_in_total = commissions_total.get('total_in', 0)
        commissions_out_total = commissions_total.get('total_out', 0)
        commissions_total_active = commissions_total.get('total_active', 0)

        self.context['IN'] = IN
        self.context['OUT'] = OUT
        self.context['acquireds'] = acquireds[:5]
        self.context['commissions'] = commissions[:5]
        self.context['commissions_in_total'] = commissions_in_total if commissions_in_total else 0
        self.context['commissions_out_total'] = commissions_out_total if commissions_out_total else 0
        self.context['commissions_total_active'] = commissions_total_active if commissions_total_active else 0
        self.context['affiliate'] = affiliate
        self.context['affiliate_url'] = '%s%s' % (request.META['HTTP_HOST'], reverse('affiliate_capture', kwargs={'affiliate_code': affiliate.code}))
        return render(request, self.template_name, self.context)


class AffiliateListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/affiliate-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        affiliate =  getattr(user, 'affiliate', None)

        if not affiliate:
            affiliate = Affiliate.objects.create(user=user)
            affiliate.refresh_from_db()
        
        acquireds = AffiliateAcquired.objects.filter(affiliate_id=affiliate.id).order_by('-date_created')
  
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


class AffiliateCaptureView(View):
    def get(self, request, affiliate_code=None):
        ipaddr = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ipaddr = x_forwarded_for.split(',')[0]
        else:
            ipaddr = request.META.get('REMOTE_ADDR')

        try:
            affiliate = Affiliate.objects.get(code=affiliate_code)
        except ObjectDoesNotExist:
            return redirect(reverse('home'))

        if affiliate_code and ipaddr:
            request.session['affiliate_code'] = affiliate_code
            AffiliateCapture.objects.create(code=affiliate_code, ipaddr=ipaddr)
        return redirect(reverse('boarding'))


class CommissionListView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'market/commission-list.html'
    context = dict()

    def get(self, request):
        user = request.user
        commissions = AffiliateCommission.objects \
            .prefetch_related(Prefetch('creator'), Prefetch('affiliator'), Prefetch('caused_content_type')) \
            .select_related('creator', 'affiliator', 'caused_content_type') \
            .filter(affiliator_id=user.id).order_by('-date_created')
  
        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(commissions, settings.PAGINATION_PER_PAGE)

        try:
            commissions_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            commissions_pagination = paginator.page(1)
        except EmptyPage:
            commissions_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, commissions, commissions_pagination, page_num, paginator)

        self.context['IN'] = IN
        self.context['OUT'] = OUT
        self.context['commissions'] = commissions
        self.context['commissions_pagination'] = commissions_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
