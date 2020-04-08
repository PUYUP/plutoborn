from django.urls import path

from apps.tryout.views.packet import PacketDetailView
from apps.tryout.views.simulation import (
    SimulationExamView,
    SimulationResultView,
    SimulationRankingView)

urlpatterns = [
    path('packet/<uuid:packet_uuid>/', PacketDetailView.as_view(), name='packet_detail'),
    path('simulation/<uuid:simulation_uuid>/', SimulationExamView.as_view(), name='simulation_detail'),
    path('simulation/<uuid:simulation_uuid>/result/', SimulationResultView.as_view(), name='simulation_result'),
    path('simulation/<uuid:simulation_uuid>/ranking/', SimulationRankingView.as_view(), name='simulation_ranking')
]
