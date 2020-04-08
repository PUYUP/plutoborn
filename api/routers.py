from django.urls import path, include

from .views import RootApiView

from apps.person.api import routers as person_routers
from apps.payment.api import routers as payment_routers
from apps.market.api import routers as market_routers
from apps.tryout.api import routers as tryout_routers
from apps.mypoints.api import routers as points_routers

urlpatterns = [
    path('', RootApiView.as_view(), name='api'),
    path('person/', include((person_routers, 'person'), namespace='persons')),
    path('payment/', include((payment_routers, 'payment'), namespace='payments')),
    path('market/', include((market_routers, 'market'), namespace='markets')),
    path('tryout/', include((tryout_routers, 'tryout'), namespace='tryouts')),
    path('mypoints/', include((points_routers, 'points'), namespace='mypoints')),
]
