from django.conf import settings

from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Q, Sum

from utils.generals import get_model
from apps.payment.utils.constant import SETTLEMENT, CAPTURE, PENDING, EXPIRED
from apps.payment.utils.general import money_to_coin
from utils.midtransclient.error_midtrans import MidtransAPIError

from views.console.forms import (
    TheoryForm, PacketForm, QuestionForm, ChoiceFormSetFactory,
    BundleForm)

Theory = get_model('tryout', 'Theory')
Packet = get_model('tryout', 'Packet')
Question = get_model('tryout', 'Question')
Bundle = get_model('market', 'Bundle')
TopUp = get_model('payment', 'TopUp')

SNAP = settings.SNAP


# ==========================================
# THEORY
# ==========================================
class TheoryView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/theory.html'
    context = dict()

    def get(self, request):
        theories = Theory.objects.all()
        self.context['theories'] = theories
        return render(request, self.template_name, self.context)


class TheoryEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/theory-editor.html'
    context = dict()
    form = TheoryForm

    def get(self, request, pk=None):
        try:
            queryset = Theory.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    def post(self, request, pk=None):
        try:
            queryset = Theory.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        form = self.form(request.POST)
        if queryset:
            form = self.form(request.POST, instance=queryset)

        if form.is_valid():
            fm = form.save(commit=False)
            fm.save()
            form.save_m2m()

            if queryset:
                msg = _("Materi %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Materi %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_theory'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class TheoryDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = Theory.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Materi %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_theory'))


# ==========================================
# PACKET
# ==========================================
class PacketView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/packet.html'
    context = dict()

    def get(self, request):
        packets = Packet.objects.all()
        self.context['packets'] = packets
        return render(request, self.template_name, self.context)


class PacketEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/packet-editor.html'
    context = dict()
    form = PacketForm

    def get(self, request, pk=None):
        try:
            queryset = Packet.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    def post(self, request, pk=None):
        try:
            queryset = Packet.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        form = self.form(request.POST)
        if queryset:
            form = self.form(request.POST, instance=queryset)

        if form.is_valid():
            fm = form.save(commit=False)
            fm.save()
            form.save_m2m()

            if queryset:
                msg = _("Paket %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Paket %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_packet'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class PacketDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = Packet.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Paket %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_packet'))


# ==========================================
# QUESTION
# ==========================================
class QuestionView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/question.html'
    context = dict()

    def get(self, request, packet_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        questions = Question.objects.filter(packet_id=packet_id).order_by('numbering')

        self.context['packet'] = packet
        self.context['questions'] = questions
        return render(request, self.template_name, self.context)


class QuestionReorderView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/question.html'
    context = dict()

    def get(self, request, packet_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        questions_order = packet.questions.all().order_by('id')
        questions_order_theory = packet.questions.filter(packet_id=packet.id).order_by('id')

        questions_list = list()
        questions_theory_list = list()

        for index, item in enumerate(questions_order):
            numbering = index + 1
            setattr(item, 'numbering', numbering)
            questions_list.append(item)

        for index, item in enumerate(questions_order_theory):
            numbering = index + 1
            setattr(item, 'numbering_local', numbering)
            questions_theory_list.append(item)

        Question.objects.bulk_update(questions_list, ['numbering'])
        Question.objects.bulk_update(questions_theory_list, ['numbering_local'])
        return redirect(reverse('dashboard_question', kwargs={'packet_id': packet.id}))


class QuestionEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/question-editor.html'
    context = dict()
    form = QuestionForm
    formset = ChoiceFormSetFactory

    def get(self, request, packet_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        try:
            queryset = Question.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        identifiers = ['A', 'B', 'C', 'D', 'E']
        self.context['form'] = self.form(instance=queryset)
        self.context['formset'] = self.formset(instance=queryset, initial=[{'identifier': x} for x in identifiers])
        self.context['queryset'] = queryset
        self.context['packet'] = packet
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    def post(self, request, packet_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        try:
            queryset = Question.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        form = self.form(request.POST)
        formset = self.formset(request.POST)
        if queryset:
            form = self.form(request.POST, instance=queryset)
            formset = self.formset(request.POST, instance=queryset)

        if form.is_valid() and formset.is_valid():
            fm = form.save(commit=False)
            fm.packet = packet
            fm.save()

            fmset = formset.save(commit=False)
            for f in fmset:
                f.question = fm
                f.save()

            if queryset:
                msg = _("Pertanyaan %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Pertanyaan %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_question', kwargs={'packet_id': packet_id}))

        self.context['form'] = form
        self.context['formset'] = formset
        self.context['queryset'] = queryset
        self.context['packet'] = packet
        return render(request, self.template_name, self.context)


class QuestionDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, packet_id=None, pk=None):
        try:
            queryset = Question.objects.get(pk=pk, packet_id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_question', kwargs={'packet_id': packet_id}))

        queryset.delete()
        msg = _("Pertanyaan %s berhasil dihapus." % (queryset.label))
        messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_question', kwargs={'packet_id': packet_id}))


# ==========================================
# BUNDLE
# ==========================================
class BundleView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/bundle.html'
    context = dict()

    def get(self, request):
        bundles = Bundle.objects.all()
        self.context['bundles'] = bundles
        return render(request, self.template_name, self.context)


class BundleEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/bundle-editor.html'
    context = dict()
    form = BundleForm

    def get(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    def post(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        form = self.form(request.POST)
        if queryset:
            form = self.form(request.POST, instance=queryset)

        if form.is_valid():
            fm = form.save(commit=False)
            fm.save()
            form.save_m2m()

            if queryset:
                msg = _("Bundel %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Bundel %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_bundle'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class BundleDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk=None):
        try:
            queryset = Bundle.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Bundel %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_bundle'))


# ==========================================
# TOPUP
# ==========================================
class TopUpView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/topup.html'
    context = dict()

    def get(self, request):
        topups = TopUp.objects.all().order_by('-date_created')
        self.context['topups'] = topups
        return render(request, self.template_name, self.context)


class TopUpDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/topup-detail.html'
    context = dict()

    def get(self, request, pk=None):
        try:
            topup = TopUp.objects.get(id=pk)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_topup'))

        coin = money_to_coin(topup.payment_amount)

        if topup.payment_status != SETTLEMENT and topup.payment_status != CAPTURE and topup.payment_status != EXPIRED:
            try:
                payment_object = SNAP.transactions.status(topup.payment_order_id)
            except MidtransAPIError as e:
                payment_object = None

            if payment_object:
                payment_status = payment_object.get('transaction_status', None)
                payment_paid_date = payment_object.get('settlement_time', timezone.now())

                if payment_status == SETTLEMENT:
                    topup.payment_paid_date = payment_paid_date
                    topup.payment_status = SETTLEMENT

                if payment_status == 'expire' or payment_status == EXPIRED:
                    topup.payment_status = EXPIRED

                topup.save()
                topup.refresh_from_db()

        self.context['SETTLEMENT'] = SETTLEMENT
        self.context['CAPTURE'] = CAPTURE
        self.context['EXPIRED'] = EXPIRED
        self.context['topup'] = topup
        self.context['coin'] = coin
        return render(request, self.template_name, self.context)
