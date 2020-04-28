from .abstract import *

# PROJECT UTILS
from utils.generals import is_model_registered

__all__ = list()

# 0
if not is_model_registered('cms', 'banner'):
    class CMSBanner(AbstractCMSBanner):
        class Meta(AbstractCMSBanner.Meta):
            db_table = 'cms_baner'

    __all__.append('CMSBanner')


# 1
if not is_model_registered('cms', 'CMSVideo'):
    class CMSVideo(AbstractCMSVideo):
        class Meta(AbstractCMSVideo.Meta):
            db_table = 'cms_video'

    __all__.append('CMSVideo')
