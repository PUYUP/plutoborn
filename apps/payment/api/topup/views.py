from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from rest_framework import status as response_status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model, random_string
from apps.payment.utils.constant import SETTLEMENT, OUT

from .serializers import TopUpSerializer

TopUp = get_model('payment', 'TopUp')
AffiliateCommission = get_model('market', 'AffiliateCommission')

# Midtrans
snap = settings.SNAP


class TopUpApiView(viewsets.ViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    @method_decorator(never_cache)
    @transaction.atomic
    def create(self, request, format=None):
        context = {'request': request}
        serializer = TopUpSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_400_BAD_REQUEST)

    # Request Midtrans SNAP
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated],
            url_path='request', url_name='request')
    def request(self, request):
        data = request.data
        nominal = data.get('nominal', None)
        description = _("Topup")

        try:
            nominal = int(nominal)
        except ValueError:
            raise NotAcceptable(_("Nominal invalid."))

        if nominal < 25000:
            raise NotAcceptable(_("Nominal tidak boleh kurang dari Rp 25.000,-"))

        # Payment data
        param = {
            "transaction_details": {
                "order_id": "TOPUP-%s" % (random_string()),
                "gross_amount": nominal
            },
            "item_details": str(description),
            "customer_details": {
                "first_name": request.user.username,
                "email": request.user.email
            },
            'expiry': {
				"unit": "day",
				"duration": 1
            },
            "credit_card": {
                "secure": True
            }
        }

        # create transaction
        transaction = snap.create_transaction(param)
        transaction_token = transaction.get('token', '')
        return Response({'token': transaction_token}, status=response_status.HTTP_201_CREATED)

    # Pay with commission
    @method_decorator(never_cache)
    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated],
            url_path='commission', url_name='commission')
    def commission(self, request):
        data = request.data
        user = request.user

        # check user has affiliate
        affiliate =  getattr(user, 'affiliate', None)
        if not affiliate:
            raise NotAcceptable(_("Anda belum menjadi Affiliasi. Kunjungi laman Affiliate."))

        commission_amounts = user.account.commission_amounts
        commission_active = commission_amounts.get('total_active', 0)
        nominal = data.get('nominal', None)
        description = _("Topup")

        try:
            nominal = int(nominal)
        except ValueError:
            raise NotAcceptable(_("Nominal invalid."))

        if nominal < 25000:
            raise NotAcceptable(_("Nominal tidak boleh kurang dari Rp 25.000,-"))

        if nominal > commission_active:
            raise NotAcceptable(_("Komisi Anda tidak cukup. Saat ini ada Rp %s" % commission_active))

        topup = TopUp.objects.create(
            payment_type='commission',
            payment_amount=nominal,
            payment_created_date=timezone.now(),
            payment_paid_date=timezone.now(),
            payment_status=SETTLEMENT,
            is_used=True,
            user=user
        )

        description = _("Digunakan untuk Topup sejumlah %s" % (nominal))
        caused_content_type = ContentType.objects \
            .get_for_model(topup, for_concrete_model=False)

        AffiliateCommission.objects.create(
            amount=nominal, creator=user, affiliator=user, transaction_type=OUT, description=description,
            caused_object_id=topup.id, caused_content_type=caused_content_type)

        return Response({'detail': _("Success!")}, status=response_status.HTTP_201_CREATED)
