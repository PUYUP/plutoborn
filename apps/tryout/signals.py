from django.db.models import Q, Count, Sum
from django.core.exceptions import ValidationError

from utils.generals import get_model

Choice = get_model('tryout', 'Choice')
Question = get_model('tryout', 'Question')


def choice_handler(sender, instance, created, **kwargs):
    pass

def question_handler(sender, instance, created, **kwargs):
    packet = instance.packet
    theories = Question.objects.filter(packet_id=packet.id) \
        .distinct() \
        .values('theory', 'theory__duration') \
        .aggregate(total_duration=Sum('theory__duration'))

    packet.duration = theories['total_duration']
    packet.save()

    """
    if created:
        packet = instance.packet
        questions = packet.questions.all().order_by('id')
        questions_theory = packet.questions.filter(packet_id=instance.packet.id).order_by('id')
        theory = Question.objects.filter(packet_id=packet.id) \
            .annotate(Count('theory', distinct=True)) \
            .values('theory', 'theory__duration')

        questions_list = list()
        questions_theory_list = list()

        for index, item in enumerate(questions):
            numbering = index + 1
            setattr(item, 'numbering', numbering)
            questions_list.append(item)

        for index, item in enumerate(questions_theory):
            numbering = index + 1
            setattr(item, 'numbering_local', numbering)
            questions_theory_list.append(item)

        Question.objects.bulk_update(questions_list, ['numbering'])
        Question.objects.bulk_update(questions_theory_list, ['numbering_local'])
    """
    pass


def question_delete_handler(sender, instance, using, **kwargs):
    """
    packet = instance.packet
    questions = packet.questions.all().order_by('id')
    questions_theory = packet.questions.filter(packet_id=instance.packet.id).order_by('id')
    theory = Question.objects.filter(packet_id=packet.id) \
        .annotate(Count('theory', distinct=True)) \
        .values('theory', 'theory__duration')

    questions_list = list()
    questions_theory_list = list()

    for index, item in enumerate(questions):
        numbering = index + 1
        setattr(item, 'numbering', numbering)
        questions_list.append(item)

    for index, item in enumerate(questions_theory):
        numbering = index + 1
        setattr(item, 'numbering_local', numbering)
        questions_theory_list.append(item)

    Question.objects.bulk_update(questions_list, ['numbering'])
    Question.objects.bulk_update(questions_theory_list, ['numbering_local'])
    """
    pass
