from django.apps import AppConfig

from django.db.models.signals import post_save, post_delete


class TryoutConfig(AppConfig):
    name = 'apps.tryout'

    def ready(self):
        from utils.generals import get_model
        from apps.tryout.signals import choice_handler, question_handler, question_delete_handler

        Choice = get_model('tryout', 'Choice')
        Question = get_model('tryout', 'Question')

        post_save.connect(choice_handler, sender=Choice, dispatch_uid='choice_signal')
        post_save.connect(question_handler, sender=Question, dispatch_uid='question_signal')
        post_save.connect(question_delete_handler, sender=Question, dispatch_uid='question_delete_signal')
