from django.urls import path, include

from public.views import HomeView
from public.views.console import urls as console_urls

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('console/', include(console_urls)),
]
