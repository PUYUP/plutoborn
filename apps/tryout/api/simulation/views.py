from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status as response_status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action

from utils.generals import get_model

from .serializers import SimulationSerializer

Simulation = get_model('tryout', 'Simulation')


class SimulationApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = SimulationSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        context = {'request': request}

        # Single object
        try:
            instance = Simulation.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = SimulationSerializer(
            instance, data=request.data, partial=True, context=context)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, uuid=None, format=None):
        return Response(status=response_status.HTTP_200_OK)

    # Sub-action request password reset
    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated],
            url_path='question', url_name='question')
    def question(self, request, uuid=None):
        user = request.user
        context = {'request': self.request}

        try:
            queryset = Simulation.objects.get(uuid=uuid, user_id=user.id)
        except ObjectDoesNotExist:
            raise NotFound()

        serializer = SimulationSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
