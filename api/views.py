# THIRD PARTY
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny


class RootApiView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response({
            'person': {
                'token': reverse('person:token_obtain_pair', request=request,
                                 format=format, current_app='person'),
                'token-refresh': reverse('person:token_refresh', request=request,
                                         format=format, current_app='person'),
                'users': reverse('person:user-list', request=request,
                                 format=format, current_app='person'),
                'otps': reverse('person:otp-list', request=request,
                                format=format, current_app='person'),
            },
            'payment': {
                'topups': reverse('payment:topup-list', request=request,
                                  format=format, current_app='payment'),
            },
            'market': {
                'boughts': reverse('market:bought-list', request=request,
                                   format=format, current_app='market'),
                'voucher-redeems': reverse('market:voucher_redeem-list', request=request,
                                           format=format, current_app='market'),
                'bundles': reverse('market:bundle-list', request=request,
                                   format=format, current_app='market'),
                'proofs': reverse('market:proof-list', request=request,
                                  format=format, current_app='market'),
            },
            'tryout': {
                'simulations': reverse('tryout:simulation-list', request=request,
                                       format=format, current_app='tryout'),
                'answers': reverse('tryout:answer-list', request=request,
                                   format=format, current_app='tryout'),
                'questions': reverse('tryout:question-list', request=request,
                                     format=format, current_app='tryout'),
                'attachments': reverse('tryout:attachment-list', request=request,
                                       format=format, current_app='tryout'),
            },
            'mypoints': {
                'points': reverse('mypoints:points-list', request=request,
                                  format=format, current_app='mypoints'),
            },
        })
