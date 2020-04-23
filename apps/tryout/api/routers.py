from django.urls import path, include

# THIRD PARTY
from rest_framework.routers import DefaultRouter

# LOCAL
from .simulation.views import SimulationApiView
from .answer.views import AnswerApiView
from .question.views import QuestionApiView
from .attachment.views import AttachmentApiView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('simulations', SimulationApiView, basename='simulation')
router.register('answers', AnswerApiView, basename='answer')
router.register('questions', QuestionApiView, basename='question')
router.register('attachments', AttachmentApiView, basename='attachment')

app_name = 'tryout'

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
