import datetime
import calendar

from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from rest_framework import status as response_status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.generals import get_model
from apps.market.utils.constant import PUBLISHED

from .serializers import BundleSerializer

Bundle = get_model('market', 'Bundle')


class BundleApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def list(self, request, format=None):
        context = {'request': request}
        today = datetime.datetime.today()
        month = int(request.query_params.get('month', today.month))
        year = int(request.query_params.get('year', today.year))

        try:
            last_day = calendar.monthrange(year, month)[1]
        except calendar.IllegalMonthError:
            return Response(status=response_status.HTTP_403_FORBIDDEN)
        
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, last_day)

        queryset = Bundle.objects.filter(start_date__range=(start_date, end_date), status=PUBLISHED)
        serializer = BundleSerializer(queryset, many=True, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
