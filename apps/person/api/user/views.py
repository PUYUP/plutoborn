from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.validators import validate_email

# THIRD PARTY
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status as response_status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, NotAcceptable
from rest_framework.pagination import PageNumberPagination

# JWT
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

# SERIALIZERS
from .serializers import (
    UserSerializer,
    SingleUserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer)

# GET MODELS FROM GLOBAL UTILS
from utils.generals import get_model

Account = get_model('person', 'Account')

# Define to avoid used ...().paginate__
PAGINATOR = PageNumberPagination()


class UserApiView(viewsets.ViewSet):
    lookup_field = 'id'
    permission_classes = (AllowAny,)
    permission_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'partial_update': [IsAuthenticated]
    }

    def get_permissions(self):
        """
        Instantiates and returns
        the list of permissions that this view requires.
        """
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_action
                    [self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    # Get a objects
    def get_object(self, id=None):
        # Single object
        if id:
            try:
                return User.objects.get(id=id)
            except ObjectDoesNotExist:
                raise NotFound()

        # All objects
        return User.objects.prefetch_related(Prefetch('account'), Prefetch('profile')) \
            .select_related('account', 'profile') \
            .all()

    # Return a response
    def get_response(self, serializer, serializer_parent=None):
        response = dict()
        response['count'] = PAGINATOR.page.paginator.count
        response['navigate'] = {
            'previous': PAGINATOR.get_previous_link(),
            'next': PAGINATOR.get_next_link()
        }
        response['results'] = serializer.data
        return Response(response, status=response_status.HTTP_200_OK)

    # All Users
    def list(self, request, format=None):
        context = {'request': self.request}
        queryset = self.get_object()
        queryset_paginator = PAGINATOR.paginate_queryset(queryset, request)
        serializer = UserSerializer(queryset_paginator, many=True, context=context)
        return self.get_response(serializer)

    # Single User
    @method_decorator(never_cache)
    @transaction.atomic
    def retrieve(self, request, id=None, format=None):
        context = {'request': self.request}
        queryset = self.get_object(id=id)
        serializer = SingleUserSerializer(queryset, many=False, context=context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    # Register User
    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': self.request}
        serializer = CreateUserSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    # Update basic user data
    @method_decorator(never_cache)
    @transaction.atomic
    def partial_update(self, request, id=None, format=None):
        context = {'request': self.request}

        # Single object
        try:
            instance = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise NotFound()

        # Append file
        if request.FILES:
            setattr(request.data, 'files', request.FILES)

        serializer = UpdateUserSerializer(
            instance, data=request.data, partial=True, context=context)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            serializer_single = SingleUserSerializer(instance, many=False, context=context)
            return Response(serializer_single.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    # Sub-action check email available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-email', url_name='check_email')
    def check_email(self, request):
        """
        {
            "email": "my@email.com"
        }
        """
        data = request.data
        email = data.get('email', None)
        if not email:
            raise NotFound(_("Email not provided."))

        try:
            validate_email(email)
        except ValidationError as e:
            raise NotAcceptable(_(''.join(e.messages)))

        try:
            Account.objects.get(email=email, email_verified=True)
            raise NotAcceptable(_("Email has used."))
        except ObjectDoesNotExist:
            return Response({'detail': _("Passed!")}, status=response_status.HTTP_200_OK)

    # Sub-action check telephone available
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[AllowAny],
            url_path='check-telephone', url_name='check_telephone')
    def check_telephone(self, request):
        """
        {
            "telephone": "1234567890"
        }
        """
        data = request.data
        telephone = data.get('telephone', None)
        if not telephone:
            raise NotFound(_("Telephone not provided."))

        try:
            Account.objects.get(telephone=telephone, telephone_verified=True)
            raise NotAcceptable(_("Telephone has used."))
        except ObjectDoesNotExist:
            return Response({'detail': _("Passed!")}, status=response_status.HTTP_200_OK)


class TokenObtainPairSerializerExtend(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user:
            data['id'] = self.user.id
            data['username'] = self.user.username
        return data


class TokenObtainPairViewExtend(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerExtend

    @method_decorator(never_cache)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Make user logged-in
        if settings.SESSION_LOGIN:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

        return Response(serializer.validated_data, status=response_status.HTTP_200_OK)
