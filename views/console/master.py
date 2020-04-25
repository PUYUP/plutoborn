import pandas as pd
import numpy as np

from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, Sum, Prefetch
from django.contrib.contenttypes.models import ContentType

from utils.generals import get_model
from apps.payment.utils.constant import SETTLEMENT, CAPTURE, PENDING, EXPIRED
from apps.payment.utils.general import money_to_coin
from utils.midtransclient.error_midtrans import MidtransAPIError

from views.console.forms import (
    TheoryForm, PacketForm, QuestionForm, ChoiceFormSetFactory, CategoryForm,
    QuestionImportForm
)

Category = get_model('tryout', 'Category')
Theory = get_model('tryout', 'Theory')
Packet = get_model('tryout', 'Packet')
Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')
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

    @transaction.atomic
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

    @transaction.atomic
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
# CATEGORY
# ==========================================
class CategoryView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/category.html'
    context = dict()

    def get(self, request):
        categories = Category.objects.all()
        self.context['categories'] = categories
        return render(request, self.template_name, self.context)


class CategoryEditorView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/category-editor.html'
    context = dict()
    form = CategoryForm

    def get(self, request, pk=None):
        try:
            queryset = Category.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        self.context['form'] = self.form(instance=queryset)
        self.context['queryset'] = queryset
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, pk=None):
        try:
            queryset = Category.objects.get(pk=pk)
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
                msg = _("Kategori %s berhasil diperbarui." % fm.label)
            else:
                msg = _("Kategori %s berhasil dibuat." % fm.label)
            messages.add_message(request, messages.INFO, msg)

            return redirect(reverse('dashboard_category'))

        self.context['form'] = form
        return render(request, self.template_name, self.context)


class CategoryDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    @transaction.atomic
    def get(self, request, pk=None):
        try:
            queryset = Category.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        if queryset:
            queryset.delete()
            msg = _("Kategory %s berhasil dihapus." % (queryset.label))
            messages.add_message(request, messages.WARNING, msg)
        return redirect(reverse('dashboard_category'))


# ==========================================
# PACKET
# ==========================================
class PacketView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/packet.html'
    context = dict()

    def get(self, request):
        packets = Packet.objects \
            .prefetch_related(Prefetch('category'), Prefetch('theories')) \
            .select_related('category') \
            .all()

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

    @transaction.atomic
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

    @transaction.atomic
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
    form = QuestionImportForm

    def get(self, request, packet_id=None, theory_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        questions = Question.objects \
            .prefetch_related(Prefetch('packet'), Prefetch('theory')) \
            .select_related('packet', 'theory') \
            .filter(packet_id=packet_id).order_by('numbering')
        if theory_id:
            questions = questions.filter(theory_id=theory_id)

        self.context['form'] = self.form()
        self.context['theory_id'] = theory_id
        self.context['packet'] = packet
        self.context['questions'] = questions
        self.context['messages'] = messages.get_messages(request)
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, packet_id=None, theory_id=None, pk=None):
        packet = Packet.objects.get(id=packet_id)
        form = self.form(request.POST, request.FILES)

        if form.is_valid():
            combined_data = list()
            saved_data = list()
            read_data = pd.read_excel(request.FILES['file'], sheet_name='Sheet1')

            # Convert each column to list()
            theories = read_data['MATERI'].tolist()
            sub_theories = read_data['SUB_MATERI'].tolist()
            numberings = read_data['NOMOR'].tolist()
            questions = read_data['PERTANYAAN'].tolist()
            descriptions = read_data['KETERANGAN'].tolist()
            explanations = read_data['PEMBAHASAN'].tolist()
            choices_a = read_data['A'].tolist()
            choices_b = read_data['B'].tolist()
            choices_c = read_data['C'].tolist()
            choices_d = read_data['D'].tolist()
            choices_e = read_data['E'].tolist()
            choices_true = read_data['BENAR'].tolist()
            scores_a = read_data['SKOR_A'].tolist()
            scores_b = read_data['SKOR_B'].tolist()
            scores_c = read_data['SKOR_C'].tolist()
            scores_d = read_data['SKOR_D'].tolist()
            scores_e = read_data['SKOR_E'].tolist()

            # Combined here
            for index, item in enumerate(questions):
                data = {
                    'packet': packet.pk,
                    'numbering': numberings[index],
                    'label': questions[index],
                    'theory': theories[index],
                    'sub_theory': sub_theories[index],
                    'description': descriptions[index],
                    'explanation': explanations[index],
                }

                right_choice = choices_true[index] if choices_true[index] else ''
                choices = list()
                for idx, itm in enumerate(choices_a):
                    x = {
                        'A': {
                            'label': choices_a[idx],
                            'score': int(scores_a[idx]) if not np.isnan(scores_a[idx]) else '',
                            'right_choice': right_choice == 'A',
                        },
                        'B': {
                            'label': choices_b[idx],
                            'score': int(scores_b[idx]) if not np.isnan(scores_b[idx]) else '',
                            'right_choice': right_choice == 'B',
                        },
                        'C': {
                            'label': choices_c[idx],
                            'score': int(scores_c[idx]) if not np.isnan(scores_c[idx]) else '',
                            'right_choice': right_choice == 'C',
                        },
                        'D': {
                            'label': choices_d[idx],
                            'score': int(scores_d[idx]) if not np.isnan(scores_d[idx]) else '',
                            'right_choice': right_choice == 'D',
                        },
                        'E': {
                            'label': choices_e[idx],
                            'score': int(scores_e[idx]) if not np.isnan(scores_e[idx]) else '',
                            'right_choice': right_choice == 'E',
                        },
                    }
                    choices.append(x)

                data['question_%s' % index] = choices[index]
                combined_data.append(data)

            # Prepare create
            for index, item in enumerate(combined_data):
                try:
                    theory_object = Theory.objects.get(label=item['theory'])
                except ObjectDoesNotExist:
                    theory_object = None

                try:
                    sub_theory_object = Theory.objects.get(label=item['sub_theory'])
                except ObjectDoesNotExist:
                    sub_theory_object = None

                data = Question(
                    packet=packet,
                    label=item['label'],
                    theory=theory_object,
                    sub_theory=sub_theory_object,
                    description=item['description'],
                    explanation=item['explanation'],
                )
                saved_data.append(data)

            # Save all!
            Question.objects.bulk_create(saved_data)

            # Prepare assign choice to question
            questions = packet.questions \
                .prefetch_related(Prefetch('packet'), Prefetch('theory')) \
                .select_related('packet', 'theory') \
                .all()

            qcount = questions.count()
            if questions.exists():
                questions = questions[qcount-len(combined_data):qcount]
   
            for index, question in enumerate(questions):
                choices_object = list()
                q = combined_data[index]
                choices = q['question_%s' % index]

                for identifier in choices:
                    itm = choices[identifier]
                    c = Choice(
                        identifier=identifier,
                        label=itm['label'],
                        right_choice=itm['right_choice'],
                        packet=packet,
                        question=question,
                    )

                    if itm['score']:
                        setattr(c, 'score', itm['score'])
                    choices_object.append(c)

                # create choices
                Choice.objects.bulk_create(choices_object)

        msg = _("Import %s pertanyaan berhasil." % len(combined_data))
        messages.add_message(request, messages.INFO, msg)
        return redirect(reverse('dashboard_question_reorder', kwargs={'packet_id': packet_id}))


class QuestionReorderView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/question.html'
    context = dict()

    def get(self, request, packet_id=None, theory_id=None, pk=None):
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

    def get(self, request, packet_id=None, theory_id=None, pk=None):
        try:
            packet = Packet.objects.get(id=packet_id)
        except ObjectDoesNotExist:
            return redirect(reverse('dashboard_packet'))

        try:
            queryset = Question.objects.get(pk=pk)
        except ObjectDoesNotExist:
            queryset = None

        question_form = self.form(instance=queryset)
        if theory_id:
            question_form = self.form(instance=queryset, initial={'theory': theory_id})

        identifiers = ['A', 'B', 'C', 'D', 'E']
        question_ct = ContentType.objects.get(app_label="tryout", model="question")

        self.context['form'] = question_form
        self.context['formset'] = self.formset(instance=queryset, initial=[{'identifier': x} for x in identifiers])
        self.context['queryset'] = queryset
        self.context['packet'] = packet
        self.context['messages'] = messages.get_messages(request)
        self.context['question_ct'] = question_ct
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, packet_id=None, theory_id=None, pk=None):
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

            return redirect(reverse('dashboard_theory_question', kwargs={'packet_id': packet_id, 'theory_id': fm.theory.id}))

        self.context['form'] = form
        self.context['formset'] = formset
        self.context['queryset'] = queryset
        self.context['packet'] = packet
        return render(request, self.template_name, self.context)


class QuestionDeleteView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    @transaction.atomic
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
# TOPUP
# ==========================================
class TopUpView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'console/master/topup.html'
    context = dict()

    def get(self, request):
        topups = TopUp.objects \
            .prefetch_related(Prefetch('user')) \
            .select_related('user') \
            .order_by('-date_created')
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
