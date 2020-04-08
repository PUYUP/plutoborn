from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault

Answer = get_model('tryout', 'Answer')


class AnswerSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Answer
        fields = ('user', 'question', 'choice',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()
        
        user = request.user
        question = validated_data.get('question', None)
        choice = validated_data.pop('choice', None)
        defaults = {'user_id': user.id}

        # passing simulation
        simulation = question.packet.simulations \
            .filter(user_id=user.id, is_done=False) \
            .latest('date_created')

        simulation_dict = {'simulation': simulation}
        validated_data.update(simulation_dict)

        choice_dict = {'choice_id': None}
        if choice:
            choice_dict = {'choice_id': choice.id}
        defaults.update(choice_dict)

        obj, _created = Answer.objects.update_or_create(**validated_data, defaults=defaults)
        return obj
