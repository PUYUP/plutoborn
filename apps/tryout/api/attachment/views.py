from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# THIRD PARTY
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import (
    FormParser, FileUploadParser, MultiPartParser)
from rest_framework import status as response_status, viewsets

# SERIALIZERS
from .serializers import (
    AttachmentSerializer, CreateAttachmentSerializer)

# PROJECT UTILS
from utils.generals import get_model

Attachment = get_model('tryout', 'Attachment')


class AttachmentApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    parser_class = (FormParser, FileUploadParser, MultiPartParser,)

    # Create object
    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': self.request}
        serializer = CreateAttachmentSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            attachment = serializer.save()
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)
