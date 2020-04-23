from django.db import models

from .abstract import *
from .voucher import *
from .affiliate import *
from utils.generals import is_model_registered


__all__ = []

# 0
if not is_model_registered('market', 'Bundle'):
    class Bundle(AbstractBundle):
        class Meta(AbstractBundle.Meta):
            db_table = 'market_bundle'

    __all__.append('Bundle')


# 1
if not is_model_registered('market', 'Bought'):
    class Bought(AbstractBought):
        class Meta(AbstractBought.Meta):
            db_table = 'market_bought'

    __all__.append('Bought')


# 2
if not is_model_registered('market', 'Voucher'):
    class Voucher(AbstractVoucher):
        class Meta(AbstractVoucher.Meta):
            db_table = 'market_voucher'

    __all__.append('Voucher')


# 3
if not is_model_registered('market', 'VoucherRedeem'):
    class VoucherRedeem(AbstractVoucherRedeem):
        class Meta(AbstractVoucherRedeem.Meta):
            db_table = 'market_voucher_redeem'

    __all__.append('VoucherRedeem')


# 4
if not is_model_registered('market', 'BundlePasswordPassed'):
    class BundlePasswordPassed(AbstractBundlePasswordPassed):
        class Meta(AbstractBundlePasswordPassed.Meta):
            db_table = 'market_bundle_passoword_passed'

    __all__.append('BundlePasswordPassed')


# 5
if not is_model_registered('market', 'Affiliate'):
    class Affiliate(AbstractAffiliate):
        class Meta(AbstractAffiliate.Meta):
            db_table = 'market_affiliate'

    __all__.append('Affiliate')


# 6
if not is_model_registered('market', 'AffiliateAcquired'):
    class AffiliateAcquired(AbstractAffiliateAcquired):
        class Meta(AbstractAffiliateAcquired.Meta):
            db_table = 'market_affiliate_acquired'

    __all__.append('AffiliateAcquired')


# 7
if not is_model_registered('market', 'AffiliateCommission'):
    class AffiliateCommission(AbstractAffiliateCommission):
        class Meta(AbstractAffiliateCommission.Meta):
            db_table = 'market_affiliate_commission'

    __all__.append('AffiliateCommission')


# 8
if not is_model_registered('market', 'AffiliateCapture'):
    class AffiliateCapture(AbstractAffiliateCapture):
        class Meta(AbstractAffiliateCapture.Meta):
            db_table = 'market_affiliate_capture'

    __all__.append('AffiliateCapture')


# 9
if not is_model_registered('market', 'BoughtProofRequirement'):
    class BoughtProofRequirement(AbstractBoughtProofRequirement):
        class Meta(AbstractBoughtProofRequirement.Meta):
            db_table = 'market_bought_proof_requirement'

    __all__.append('BoughtProofRequirement')


# 10
if not is_model_registered('market', 'BoughtProof'):
    class BoughtProof(AbstractBoughtProof):
        class Meta(AbstractBoughtProof.Meta):
            db_table = 'market_bought_proof'

    __all__.append('BoughtProof')


# 11
if not is_model_registered('market', 'BoughtProofDocument'):
    class BoughtProofDocument(AbstractBoughtProofDocument):
        class Meta(AbstractBoughtProofDocument.Meta):
            db_table = 'market_bought_proof_document'

    __all__.append('BoughtProofDocument')
