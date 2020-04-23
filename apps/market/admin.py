from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from utils.generals import get_model

Bundle = get_model('market', 'Bundle')
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


# Register your models here.
admin.site.register(Bundle, BundleExtend)
admin.site.register(Bought)
admin.site.register(Voucher)
admin.site.register(VoucherRedeem)
admin.site.register(Affiliate)
admin.site.register(AffiliateAcquired)
admin.site.register(AffiliateCommission)
admin.site.register(AffiliateCapture)
admin.site.register(BoughtProof, BoughtProofExtend)
admin.site.register(BoughtProofRequirement)
admin.site.register(BoughtProofDocument)
