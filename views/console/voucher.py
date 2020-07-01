from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Coalesce
from django.db.models import Q, F, Sum, Count, Case, When, Value, Subquery, OuterRef, IntegerField

from utils.pagination import Pagination
from utils.generals import get_model

Voucher = get_model('market', 'Voucher')


@method_decorator(login_required, name='dispatch')
class VoucherListView(View):
    template_name = 'console/voucher/list.html'
    context = dict()

    def get(self, request):
        vouchers = Voucher.objects \
            .annotate(
                total_redeem=Coalesce(Count('voucher_redeems'), 0)
            ).order_by('-total_redeem')

        # paginator
        page_num = int(self.request.GET.get('p', 0))
        paginator = Paginator(vouchers, settings.PAGINATION_PER_PAGE)

        try:
            vouchers_pagination = paginator.page(page_num + 1)
        except PageNotAnInteger:
            vouchers_pagination = paginator.page(1)
        except EmptyPage:
            vouchers_pagination = paginator.page(paginator.num_pages)

        pagination = Pagination(request, vouchers, vouchers_pagination, page_num, paginator)

        self.context['vouchers'] = vouchers
        self.context['vouchers_total'] = vouchers.count()
        self.context['vouchers_pagination'] = vouchers_pagination
        self.context['pagination'] = pagination
        return render(request, self.template_name, self.context)
