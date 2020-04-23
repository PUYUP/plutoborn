from django.db import models

from .abstract import *
from .simulation import *
from utils.generals import is_model_registered


__all__ = []

# 0
if not is_model_registered('tryout', 'Theory'):
    class Theory(AbstractTheory):
        class Meta(AbstractTheory.Meta):
            db_table = 'tryout_theory'

    __all__.append('Theory')


# 1
if not is_model_registered('tryout', 'Packet'):
    class Packet(AbstractPacket):
        class Meta(AbstractPacket.Meta):
            db_table = 'tryout_packet'

    __all__.append('Packet')


# 2
if not is_model_registered('tryout', 'Question'):
    class Question(AbstractQuestion):
        class Meta(AbstractQuestion.Meta):
            db_table = 'tryout_question'

    __all__.append('Question')


# 3
if not is_model_registered('tryout', 'Choice'):
    class Choice(AbstractChoice):
        class Meta(AbstractChoice.Meta):
            db_table = 'tryout_choice'

    __all__.append('Choice')


# 4
if not is_model_registered('tryout', 'Answer'):
    class Answer(AbstractAnswer):
        class Meta(AbstractAnswer.Meta):
            db_table = 'tryout_answer'

    __all__.append('Answer')


# 5
if not is_model_registered('tryout', 'Acquired'):
    class Acquired(AbstractAcquired):
        class Meta(AbstractAcquired.Meta):
            db_table = 'tryout_acquired'

    __all__.append('Acquired')


# 6
if not is_model_registered('tryout', 'Simulation'):
    class Simulation(AbstractSimulation):
        class Meta(AbstractSimulation.Meta):
            db_table = 'tryout_simulation'

    __all__.append('Simulation')


# 7
if not is_model_registered('tryout', 'ProgramStudy'):
    class ProgramStudy(AbstractProgramStudy):
        class Meta(AbstractProgramStudy.Meta):
            db_table = 'tryout_program_study'

    __all__.append('ProgramStudy')


# 8
if not is_model_registered('tryout', 'Category'):
    class Category(AbstractCategory):
        class Meta(AbstractCategory.Meta):
            db_table = 'tryout_category'

    __all__.append('Category')


# 9
if not is_model_registered('tryout', 'Attachment'):
    class Attachment(AbstractAttachment):
        class Meta(AbstractAttachment.Meta):
            db_table = 'tryout_attachment'

    __all__.append('Attachment')
