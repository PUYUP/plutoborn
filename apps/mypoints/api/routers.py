from django.urls import path, include

# THIRD PARTY
from rest_framework.routers import DefaultRouter

# LOCAL
from .points.views import PointsApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('points', PointsApiView, basename='points')

app_name = 'mypoints'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
