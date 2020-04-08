from django.urls import path

from apps.mypoints.views.points import PointsListView

urlpatterns = [
    path('points/', PointsListView.as_view(), name='points_list'),
]
