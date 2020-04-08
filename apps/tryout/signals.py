from django.db.models import Q
from django.core.exceptions import ValidationError

from utils.generals import get_model

Choice = get_model('tryout', 'Choice')
Question = get_model('tryout', 'Question')


def choice_handler(sender, instance, created, **kwargs):
    pass

def question_handler(sender, instance, created, **kwargs):
    pass
