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
from apps.person.forms import ProfileForm


class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'person/profile.html'
    form = ProfileForm
    context = dict()

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        account = getattr(user, 'account', None)

        born_date = ''
        if profile.born_date:
            born_date = profile.born_date.strftime('%d-%m-%Y')

        initial = {
            'full_name': user.first_name,
            'born_place': profile.born_place,
            'born_date': born_date,
            'school_origin': profile.school_origin,
            'graduation_year': profile.graduation_year,
            'whatsapp': profile.whatsapp,
            'instagram': profile.instagram,
            'telephone': account.telephone,
        }

        # messages
        self.context['messages'] = messages.get_messages(request)
        self.context['form'] = self.form(initial=initial)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request):
        form = self.form(request.POST)
        user = request.user
        profile = getattr(user, 'profile', None)
        account = getattr(user, 'account', None)

        if form.is_valid():
            full_name = form.cleaned_data.get('full_name', None)
            born_place = form.cleaned_data.get('born_place', None)
            born_date = form.cleaned_data.get('born_date', None)
            whatsapp = form.cleaned_data.get('whatsapp', None)
            school_origin = form.cleaned_data.get('school_origin', None)
            graduation_year = form.cleaned_data.get('graduation_year', None)
            instagram = form.cleaned_data.get('instagram', None)
            telephone = form.cleaned_data.get('telephone', None)

            user.first_name = full_name
            user.save()

            if account:
                account.telephone = telephone
                account.save()

            if profile:
                profile.born_place = born_place
                profile.born_date = born_date
                profile.school_origin = school_origin
                profile.graduation_year = graduation_year
                profile.whatsapp = whatsapp
                profile.instagram = instagram
                profile.save()

            # create message
            messages.add_message(request, messages.INFO, _("Berhasil menyimpan. Anda sudah bisa mengikuti Try Out."))
            return redirect(reverse('profile'))
        else:
            messages.add_message(request, messages.ERROR, _("Gagal. Data tidak lengkap."))

        # messages
        self.context['messages'] = messages.get_messages(request)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
