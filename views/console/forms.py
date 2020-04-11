from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from utils.generals import get_model
from apps.tryout.utils.constant import PREFERENCE

Theory = get_model('tryout', 'Theory')
Packet = get_model('tryout', 'Packet')
Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')
Bundle = get_model('market', 'Bundle')


class TheoryForm(forms.ModelForm):
    class Meta:
        model = Theory
        fields = '__all__'
        exclude = ('start_date', 'end_date', 'parent',)
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }


class PacketForm(forms.ModelForm):
    class Meta:
        model = Packet
        fields = '__all__'
        exclude = ('start_date', 'end_date', 'duration',)
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('packet', 'sub_theory',)
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }


class ChoiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identifier'].widget.attrs['readonly'] = True

    class Meta:
        model = Choice
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'explanation': forms.Textarea(attrs={'rows':3}),
        }


ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm, fields='__all__',
    max_num=5, min_num=5, extra=0, can_delete=False)


class ChoiceFormSetFactory(ChoiceFormSet):
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
                raise forms.ValidationError(_("Jawaban Benar hanya boleh satu."))

            if total_true == 0:
                raise forms.ValidationError(_("Harus memilih satu Jawaban Benar."))


class BundleForm(forms.ModelForm):
    class Meta:
        model = Bundle
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'packet': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        try:
            self.cleaned_data['packet']
            packets = self.cleaned_data['packet'] \
                .filter(bundle__isnull=False) \
                .exclude(bundle=self.instance) \
                .distinct()
            if packets.exists():
                raise forms.ValidationError(_("Paket yang dipilih sudah dimasukkan dalam Bundel lain."))
        except KeyError:
            pass

        return self.cleaned_data
