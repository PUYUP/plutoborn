from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Prefetch

from utils.generals import get_model

Bundle = get_model('market', 'Bundle')
BundlePasswordPassed = get_model('market', 'BundlePasswordPassed')
Bought = get_model('market', 'Bought')
BoughtProof = get_model('market', 'BoughtProof')
BoughtProofRequirement = get_model('market', 'BoughtProofRequirement')
BoughtProofDocument = get_model('market', 'BoughtProofDocument')
Packet = get_model('tryout', 'Packet')
Voucher = get_model('market', 'Voucher')
VoucherRedeem = get_model('market', 'VoucherRedeem')
Affiliate = get_model('market', 'Affiliate')
AffiliateAcquired = get_model('market', 'AffiliateAcquired')
AffiliateCommission = get_model('market', 'AffiliateCommission')
AffiliateCapture = get_model('market', 'AffiliateCapture')


class BundleAdminForm(ModelForm):
    class Meta:
        model = Bundle
        fields = '__all__'

    def clean(self):
        try:
            self.cleaned_data['packet']
            packets = self.cleaned_data['packet'] \
                .filter(bundle__isnull=False) \
                .exclude(bundle=self.instance) \
                .distinct()
            if packets.exists():
                raise ValidationError(_("Paket yang dipilih sudah dimasukkan dalam Bundel lain."))
        except KeyError:
            pass

        return self.cleaned_data


class BoughtProofDocumentInline(admin.StackedInline):
    model = BoughtProofDocument
    readonly_fields = ['user']


class BundleExtend(admin.ModelAdmin):
    model = Bundle
    form = BundleAdminForm


class BoughtProofExtend(admin.ModelAdmin):
    model = BoughtProof
    inlines = [BoughtProofDocumentInline,]


class BoughtExtend(admin.ModelAdmin):
    model = Bought
    list_display = ('bundle', 'user', 'status',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs \
            .prefetch_related(Prefetch('user'), Prefetch('bundle')) \
            .select_related('user', 'bundle')
        return queryset


class VoucherExtend(admin.ModelAdmin):
    model = Voucher

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'creator':
            # setting the user from the request object
            kwargs['initial'] = request.user.id
            # making the field readonly
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Register your models here.
admin.site.register(Bundle, BundleExtend)
admin.site.register(BundlePasswordPassed)
admin.site.register(Bought, BoughtExtend)
admin.site.register(Voucher, VoucherExtend)
admin.site.register(VoucherRedeem)
admin.site.register(Affiliate)
admin.site.register(AffiliateAcquired)
admin.site.register(AffiliateCommission)
admin.site.register(AffiliateCapture)
admin.site.register(BoughtProof, BoughtProofExtend)
admin.site.register(BoughtProofRequirement)
admin.site.register(BoughtProofDocument)
