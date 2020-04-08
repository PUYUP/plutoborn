from django.urls import path
from django.contrib.auth import views as auth_views

from apps.person.views.auth import (
    LoginView,
    SignUpView,
    VerifyView,
    BoardingView,
    EmailValidationOnForgotPassword)

from apps.person.views.profile import ProfileView
from apps.person.views.secure import SecureView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('secure/', SecureView.as_view(), name='secure'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('boarding/', BoardingView.as_view(), name='boarding'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='templates/person/auth/login.html'), name='login'),
    
    path('lost/', auth_views.PasswordResetView.as_view(template_name='templates/person/auth/lost-password.html', form_class=EmailValidationOnForgotPassword), name='password_reset'),
    path('lost/done/', auth_views.PasswordResetDoneView.as_view(template_name='templates/person/auth/lost-password-done.html'), name='password_reset_done'),
    path('lost/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='templates/person/auth/lost-password-confirm.html'), name='password_reset_confirm'),
    path('lost/success/', auth_views.PasswordResetCompleteView.as_view(template_name='templates/person/auth/lost-password-complete.html'), name='password_reset_complete'),
]
