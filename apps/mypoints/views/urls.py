from django.urls import path

from apps.mypoints.views.points import PointsView, PointsListView

urlpatterns = [
    path('points/', PointsView.as_view(), name='points'),
    path('points/all/', PointsListView.as_view(), name='points_list'),
]
