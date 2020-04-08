from django.urls import path, include

# THIRD PARTY
from rest_framework.routers import DefaultRouter

# LOCAL
from .topup.views import TopUpApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('topups', TopUpApiView, basename='topup')

app_name = 'payment'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
