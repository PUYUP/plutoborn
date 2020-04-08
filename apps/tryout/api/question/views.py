from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Count, Prefetch, Case, When, Value, BooleanField, IntegerField,
    F, Q, Subquery, OuterRef)

from rest_framework import status as response_status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from utils.generals import get_model

from .serializers import QuestionSerializer

Question = get_model('tryout', 'Question')


class QuestionApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None):
        context = {'request': self.request}

        try:
            queryset = Question.objects \
                .get(
                    uuid=uuid,
                    packet__acquireds__user_id=request.user.id,
                    packet__simulations__user_id=request.user.id,
                    packet__simulations__is_done=False
                )
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = QuestionSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
