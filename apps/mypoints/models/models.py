from .abstract import *

# PROJECT UTILS
from utils.generals import is_model_registered

__all__ = list()

# 0
if not is_model_registered('mypoints', 'Points'):
    class Points(AbstractPoints):
        class Meta(AbstractPoints.Meta):
            db_table = 'mypoints_points'

    __all__.append('Points')
