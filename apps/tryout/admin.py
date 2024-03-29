from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.db.models import Prefetch

from utils.generals import get_model
from apps.tryout.utils.constant import PREFERENCE

Theory = get_model('tryout', 'Theory')
Packet = get_model('tryout', 'Packet')
Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')
Answer = get_model('tryout', 'Answer')
Acquired = get_model('tryout', 'Acquired')
Simulation = get_model('tryout', 'Simulation')
ProgramStudy = get_model('tryout', 'ProgramStudy')
Category = get_model('tryout', 'Category')


class ChoiceInlineForm(BaseInlineFormSet):
    def clean(self):
        super().clean()

        total_true = 0
        theory = self.data.get('theory', None)
        try:
            theory_obj = Theory.objects.get(pk=theory)
        except Theory.ObjectDoesNotExist:
            theory_obj = None

        if theory_obj is None or (theory_obj and not theory_obj.scoring_type == PREFERENCE):
            for form in self.forms:
                if form.cleaned_data and form.cleaned_data.get('right_choice') == True:
                    total_true += 1

            if total_true > 1:
                raise ValidationError(_("Jawaban Benar hanya boleh satu."))

            if total_true == 0:
                raise ValidationError(_("Harus memilih satu Jawaban Benar."))


class TheoryAdmin(admin.ModelAdmin):
    model = Theory
    list_display = ('label', 'true_score', 'false_score', 'none_score',
                    'duration', 'parent',)


class ChoiceInline(admin.StackedInline):
    model = Choice
    formset = ChoiceInlineForm
    min_num = 2
    max_num = 5


class PacketAdmin(admin.ModelAdmin):
    model = Packet
    list_display = ('label', 'education_level', 'classification',
                    'passed_score', 'duration', 'chance',)


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_display = ('label', 'packet', 'theory',)
    inlines = (ChoiceInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('packet'), Prefetch('theory')) \
            .select_related('packet', 'theory')
        return queryset


class ChoiceAdmin(admin.ModelAdmin):
    model = Choice
    list_display = ('label', 'question', 'identifier',)
    readonly_fields = ('label', 'question', 'identifier', 'score', 'description',
                       'explanation', 'right_choice',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('packet'), Prefetch('question')) \
            .select_related('packet', 'question')
        return queryset


class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    list_display = ('user', 'question', 'right_choice',)
    list_filter = ('right_choice', 'packet', 'packet__questions__theory',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('user'), Prefetch('packet'), Prefetch('question'),
                              Prefetch('choice'), Prefetch('simulation')) \
            .select_related('user', 'packet', 'question', 'choice', 'simulation')
        return queryset


class SimulationAdmin(admin.ModelAdmin):
    model = Simulation
    list_display = ('packet', 'user', 'start_date', 'is_done', 'chance',)
    list_filter = ('user', 'packet',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('user'), Prefetch('packet'), Prefetch('acquired'),
                              Prefetch('program_study')) \
            .select_related('user', 'packet', 'acquired')
        return queryset


class AcquiredExtend(admin.ModelAdmin):
    model = Acquired
    list_display = ('packet', 'user', 'status',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('user'), Prefetch('packet')) \
            .select_related('user', 'packet')
        return queryset


admin.site.register(Theory, TheoryAdmin)
admin.site.register(Packet, PacketAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Acquired, AcquiredExtend)
admin.site.register(Simulation, SimulationAdmin)
admin.site.register(ProgramStudy)
admin.site.register(Category)
