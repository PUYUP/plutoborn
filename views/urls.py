from django.urls import path, include

from views import HomeView
from views.console import urls as console_urls

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('console/', include(console_urls)),
]
