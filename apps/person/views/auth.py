from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model
from apps.person.forms import (
    BoardingForm, VerifyForm, SignupForm)
from apps.person.utils.constant import REGISTER_VALIDATION
from apps.payment.utils.constant import IN

OTPCode = get_model('person', 'OTPCode')
Affiliate = get_model('market', 'Affiliate')
AffiliateAcquired = get_model('market', 'AffiliateAcquired')
Points = get_model('mypoints',  'Points')


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email_field_name = User.get_email_field_name()
        email = self.cleaned_data['email']
        if not User.objects.filter(**{'%s__iexact' % email_field_name:email}, is_active=True, account__email_verified=True).exists():
            msg = _("There is no user registered with the specified E-Mail address.")
            self.add_error('email', msg)
        return email


class LoginView(View):
    template_name = 'templates/person/auth/login.html'
    context = dict()

    def get(self, request):
        # logged-in user why access this page?
        if request.user.is_authenticated:
            return redirect(reverse('home'))

        return render(request, self.template_name, self.context)


class SignUpView(View):
    template_name = 'templates/person/auth/signup.html'
    form = SignupForm
    context = dict()

    def get(self, request):
        # logged-in user why access this page?
        if request.user.is_authenticated:
            return redirect(reverse('home'))

        email = request.session.get('email', False)
        otp_code = request.session.get('otp_code', False)
        identifier = 'register_boarding'

        # make sure OTP valid!
        try:
            otp_obj = OTPCode.objects.get(
                email=email, otp_code=otp_code, identifier=identifier,
                is_used=True, is_expired=False)
        except ObjectDoesNotExist:
            otp_obj = None

        if (not email or not otp_code) and not otp_obj:
            return redirect(reverse('boarding'))

        self.context['form'] = self.form(initial={'email': email}, request=request)
        return render(request, self.template_name, self.context)

    def post(self, request):
        email = request.session.get('email', False)
        form = self.form(request.POST, initial={'email': email}, request=request)

        # affiliate
        affiliate_code = request.session.get('affiliate_code', None)

        if form.is_valid():
            full_name = form.cleaned_data.get('full_name', None)
            username = form.cleaned_data.get('username', None)
            email = form.cleaned_data.get('email', None)
            password = form.cleaned_data.get('password2', None)

            user = User.objects.create_user(username, email, password)
            user.first_name = full_name
            user.save()
            user.refresh_from_db()

            # oh yeah, small change account
            user.account.email_verified = True
            user.account.save()
            user.account.refresh_from_db()

            # then login user
            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)

            # clear temporary session
            try:
                del request.session['otp_code']
            except KeyError:
                pass

            try:
                del request.session['email']
            except KeyError:
                pass

            # affiliate
            try:
                affiliate = Affiliate.objects.get(code=affiliate_code)
            except ObjectDoesNotExist:
                affiliate = None

            if affiliate:
                affiliate_acquired = AffiliateAcquired.objects.create(affiliate=affiliate, user_acquired=user)
                description = "Poin dari pendaftaran Affiliate oleh %s" % user.username
                amount = 5000
                caused_content_type = ContentType.objects \
                    .get_for_model(affiliate_acquired, for_concrete_model=False)

                Points.objects.create(
                    caused_object_id=affiliate_acquired.id, caused_content_type=caused_content_type,
                    user=affiliate.user, transaction_type=IN, amount=amount,
                    description=description)

            # refresh live to dashboard
            return redirect(reverse('home'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class VerifyView(View):
    template_name = 'templates/person/auth/verify.html'
    form = VerifyForm
    context = dict()

    def get(self, request):
        # logged-in user why access this page?
        if request.user.is_authenticated:
            return redirect(reverse('home'))

        # ops, secure hash not set before
        otp_hash = request.session.get('otp_hash', False)
        if not otp_hash:
            return redirect(reverse('boarding'))

        self.context['form'] = self.form(request=request)
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form(request.POST, request=request)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']

            # store otp code
            # use for signup view
            request.session['otp_code'] = otp_code

            try:
                del request.session['otp_hash']
            except KeyError:
                pass

            try:
                del request.session['identifier']
            except KeyError:
                pass

            # to signup
            return redirect(reverse('signup'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class BoardingView(View):
    template_name = 'templates/person/auth/boarding.html'
    form = BoardingForm
    context = dict()
    
    def get(self, request):
        # logged-in user why access this page?
        if request.user.is_authenticated:
            return redirect(reverse('home'))

        self.context['form'] = self.form()
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            identifier = REGISTER_VALIDATION

            _defaults = {
                'email': email,
                'identifier': identifier,
                'is_used': False,
                'is_expired': False,
            }

            obj, _created = OTPCode.objects.get_or_create(**_defaults, defaults=_defaults)

            # store secure hash to session
            request.session['otp_hash'] = obj.otp_hash
            request.session['email'] = email
            request.session['identifier'] = identifier

            # to verify
            return redirect(reverse('verify'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)
