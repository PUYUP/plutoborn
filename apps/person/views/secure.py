from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db import transaction

from utils.generals import get_model
from apps.person.forms import SecureForm


class SecureView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'person/secure.html'
    form = SecureForm
    context = dict()

    def get(self, request):
        user = request.user
        initial = {
            'email': getattr(user, 'email', '')
        }

        self.context['messages'] = messages.get_messages(request)
        self.context['form'] = self.form(initial=initial, request=request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request):
        form = self.form(request.POST, request=request)
        user = request.user
        account = getattr(user, 'account', None)

        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            password2 = form.cleaned_data.get('password2', None)

            account.email = email
            account.save()

            # change password
            if password2:
                user.set_password(password2)

            user.email = email
            user.save()

            # create message
            messages.add_message(request, messages.INFO, _("Berhasil menyimpan"))
            return redirect(reverse('secure'))

        # messages
        self.context['messages'] = messages.get_messages(request)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
