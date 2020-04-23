from django.urls import path

from views.console.dashboard import DashboardView
from views.console.master import (
    CategoryView, CategoryEditorView, CategoryDeleteView,
    TheoryView, TheoryEditorView, TheoryDeleteView,
    PacketView, PacketEditorView, PacketDeleteView,
    QuestionView, QuestionEditorView, QuestionDeleteView, QuestionReorderView,
    TopUpView, TopUpDetailView)

from views.console.bundle import (
    BundleView, BundleEditorView, BundleDeleteView, BoughtView, BoughtDetailView,
    BoughtAcceptView)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    path('category/', CategoryView.as_view(), name='dashboard_category'),
    path('category/editor/', CategoryEditorView.as_view(), name='dashboard_category_editor'),
    path('category/<int:pk>/', CategoryEditorView.as_view(), name='dashboard_category_editor'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='dashboard_category_delete'),

    path('theory/', TheoryView.as_view(), name='dashboard_theory'),
    path('theory/editor/', TheoryEditorView.as_view(), name='dashboard_theory_editor'),
    path('theory/<int:pk>/', TheoryEditorView.as_view(), name='dashboard_theory_editor'),
    path('theory/<int:pk>/delete/', TheoryDeleteView.as_view(), name='dashboard_theory_delete'),

    path('packet/', PacketView.as_view(), name='dashboard_packet'),
    path('packet/editor/', PacketEditorView.as_view(), name='dashboard_packet_editor'),
    path('packet/<int:pk>/editor/', PacketEditorView.as_view(), name='dashboard_packet_editor'),
    path('packet/<int:pk>/delete/', PacketDeleteView.as_view(), name='dashboard_packet_delete'),

    path('packet/<int:packet_id>/question/', QuestionView.as_view(), name='dashboard_question'),
    path('packet/<int:packet_id>/theory/<int:theory_id>/question/', QuestionView.as_view(), name='dashboard_theory_question'),
    path('packet/<int:packet_id>/question/reorder/', QuestionReorderView.as_view(), name='dashboard_question_reorder'),
    path('packet/<int:packet_id>/question/editor/', QuestionEditorView.as_view(), name='dashboard_question_editor'),
    path('packet/<int:packet_id>/theory/<int:theory_id>/question/editor/', QuestionEditorView.as_view(), name='dashboard_theory_question_editor'),
    path('packet/<int:packet_id>/question/<int:pk>/editor/', QuestionEditorView.as_view(), name='dashboard_question_editor'),
    path('packet/<int:packet_id>/question/<int:pk>/delete/', QuestionDeleteView.as_view(), name='dashboard_question_delete'),

    path('bundle/', BundleView.as_view(), name='dashboard_bundle'),
    path('bundle/bought/', BoughtView.as_view(), name='dashboard_bought'),
    path('bundle/bought/<int:pk>/', BoughtDetailView.as_view(), name='dashboard_bought_detail'),
    path('bundle/bought/<int:pk>/accept/', BoughtAcceptView.as_view(), name='dashboard_bought_accept'),
    path('bundle/editor/', BundleEditorView.as_view(), name='dashboard_bundle_editor'),
    path('bundle/<int:pk>/editor/', BundleEditorView.as_view(), name='dashboard_bundle_editor'),
    path('bundle/<int:pk>/delete/', BundleDeleteView.as_view(), name='dashboard_bundle_delete'),

    path('topup/', TopUpView.as_view(), name='dashboard_topup'),
    path('topup/<int:pk>/', TopUpDetailView.as_view(), name='dashboard_topup_detail'),
]
