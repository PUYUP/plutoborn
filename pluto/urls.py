from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api import routers as api_routers
from public.views import urls as public_urls
from apps.person.views import urls as person_urls
from apps.payment.views import urls as payment_urls
from apps.market.views import urls as market_urls
from apps.tryout.views import urls as tryout_urls
from apps.mypoints.views import urls as mypoints_urls

urlpatterns = [
    path('', include(public_urls)),
    path('', include(person_urls)),
    path('', include(payment_urls)),
    path('', include(market_urls)),
    path('', include(tryout_urls)),
    path('', include(mypoints_urls)),
    path('api/', include(api_routers)),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
