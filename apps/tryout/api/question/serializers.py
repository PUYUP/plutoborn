from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault

Question = get_model('tryout', 'Question')
Choice = get_model('tryout', 'Choice')


class ChoiceSerializer(serializers.ModelSerializer):
    answer_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Choice
        fields = '__all__'

    def get_answer_id(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        try:
            simulation = self.context['simulation_instance']
        except KeyError:
            simulation = obj.packet.simulations \
                .filter(user_id=request.user.id, is_done=False) \
                .latest('date_created')

        try:
            answer = obj.answers.get(user_id=request.user.id, simulation__id=simulation.id)
            return answer.id
        except ObjectDoesNotExist:
            return 0


class QuestionSerializer(serializers.ModelSerializer):
    answer_id = serializers.SerializerMethodField(read_only=True)
    choice_identifier = serializers.SerializerMethodField(read_only=True)
    prev_uuid = serializers.SerializerMethodField(read_only=True)
    next_uuid = serializers.SerializerMethodField(read_only=True)
    choices = ChoiceSerializer(many=True, read_only=True)
    scoring_type = serializers.CharField(read_only=True, source='theory.scoring_type')
    theory_label = serializers.CharField(source='theory.label')

    class Meta:
        model = Question
        fields = '__all__'

    def get_answer_id(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        try:
            simulation = self.context['simulation_instance']
        except KeyError:
            simulation = obj.packet.simulations \
                .filter(user_id=request.user.id, is_done=False) \
                .latest('date_created')

        try:
            answer = obj.answers.get(user_id=request.user.id, simulation__id=simulation.id)
            return answer.id
        except ObjectDoesNotExist:
            return 0

    def get_choice_identifier(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        try:
            simulation = self.context['simulation_instance']
        except KeyError:
            simulation = obj.packet.simulations \
                .filter(user_id=request.user.id, is_done=False) \
                .latest('date_created')

        try:
            answer = obj.answers.get(user_id=request.user.id, simulation__id=simulation.id)
            choice = getattr(answer, 'choice', None)
            return choice.identifier if choice else None
        except ObjectDoesNotExist:
            return None

    def get_prev_uuid(self, obj):
        try:
            prev_obj = obj.__class__.objects.filter(numbering__lt=obj.numbering, packet__id=obj.packet.id).last()
        except ObjectDoesNotExist:
            prev_obj = None

        if prev_obj:
            return prev_obj.uuid
        return None

    def get_next_uuid(self, obj):
        try:
            next_obj = obj.__class__.objects.filter(numbering__gt=obj.numbering, packet__id=obj.packet.id).first()
        except ObjectDoesNotExist:
            next_obj = None

        if next_obj:
            return next_obj.uuid
        return None
