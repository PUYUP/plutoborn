from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable
from rest_framework.renderers import JSONRenderer

from utils.generals import get_model
from apps.person.utils.auth import CurrentUserDefault
from apps.tryout.api.question.serializers import ChoiceSerializer, QuestionSerializer
from apps.tryout.utils.constant import LIVE
from apps.payment.utils.constant import IN, OUT
from apps.market.utils.constant import NATIONAL

Simulation = get_model('tryout', 'Simulation')
Points = get_model('mypoints',  'Points')


class SimulationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    question = serializers.SerializerMethodField(read_only=True)
    choice = serializers.SerializerMethodField(read_only=True)
    question_score = serializers.SerializerMethodField(read_only=True)
    url_result = serializers.SerializerMethodField(read_only=True)
    url_simulation = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Simulation
        fields = ('uuid', 'user', 'acquired', 'question', 'url_result', 'url_simulation', 'choice',
                  'question_score',)
        read_only_fields = ('uuid', 'url_result',
                            'url_simulation', 'choice', 'question_score',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def get_question_score(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        question_uuid = request.query_params.get('question_uuid', None)
        try:
            question = obj.packet.questions.get(uuid=question_uuid)
        except ObjectDoesNotExist:
            return None

        theory = getattr(question, 'theory', None)
        scores = {
            'true_score': theory.true_score if theory else '',
            'false_score': theory.false_score if theory else '',
            'none_score': theory.none_score if theory else ''
        }
        return scores

    def get_question(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        question_uuid = request.query_params.get('question_uuid', None)
        try:
            question = obj.packet.questions.get(uuid=question_uuid)
        except ObjectDoesNotExist:
            return None

        self.context['simulation_instance'] = obj
        serializer = QuestionSerializer(
            question, many=False, context=self.context)
        return serializer.data

    def get_choice(self, obj):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        question_uuid = request.query_params.get('question_uuid', None)
        try:
            question = obj.packet.questions.get(uuid=question_uuid)
        except ObjectDoesNotExist:
            return None

        try:
            choice = question.choices.get(right_choice=True)
        except ObjectDoesNotExist:
            choice = None

        if not choice:
            choice = question.choices.get(
                answers__user_id=request.user.id,
                answers__simulation_id=obj.id,
                answers__packet_id=obj.packet.id,
                answers__question__uuid=question_uuid
            )

        self.context['simulation_instance'] = obj
        serializer = ChoiceSerializer(choice, many=False, context=self.context)
        return serializer.data

    def get_url_result(self, obj):
        return reverse('simulation_result', kwargs={'simulation_uuid': obj.uuid})

    def get_url_simulation(self, obj):
        return reverse('simulation_detail', kwargs={'simulation_uuid': obj.uuid})

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        acquired = validated_data.get('acquired', None)
        user = validated_data.get('user', None)
        chance = acquired.packet.chance
        start_date = acquired.packet.start_date
        end_date = acquired.packet.end_date
        bundle = acquired.packet.bundle_set.first()
        classification = acquired.packet.classification
        simulation_count = Simulation.objects.filter(
            user_id=user.id, acquired_id=acquired.id).count()

        # get time from bundle
        if bundle.start_date:
            start_date = bundle.start_date

        if bundle.end_date:
            end_date = bundle.end_date

        # national simulation need program studies
        program_studies = request.data.getlist('program_studies[]', None)
        if bundle.simulation_type == NATIONAL and not program_studies:
            raise NotAcceptable(_("Program studi tidak boleh kosong."))

        # if chance not '0' indicate max chance allowed disabled
        if chance > 0 and simulation_count >= chance:
            raise NotAcceptable(_("Kesempatan telah habis."))

        # check start date if type is LIVE
        if classification == LIVE and timezone.now() < start_date:
            raise NotAcceptable(
                _("Harap tunggu. Dibuka pada %s." % start_date))

        if classification == LIVE and timezone.now() > end_date:
            raise NotAcceptable(
                _("Batas waktu telah berakhir pada %s." % end_date))

        obj, _created = Simulation.objects.get_or_create(
            **validated_data, is_done=False)

        if bundle.simulation_type == NATIONAL and program_studies:
            obj.program_study.add(*program_studies)
            obj.refresh_from_db()
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            request = self.context['request']
        except KeyError:
            raise NotAcceptable()

        user = request.user
        if instance.user.id != user.id:
            raise NotAcceptable(
                _("Anda tidak diizinkan melakukan tindakan ini."))

        instance.is_done = True
        instance.finish_date = timezone.now()
        instance.save()
        instance.refresh_from_db()

        packet = instance.packet
        bundle = packet.bundle_set.filter(packet__id=packet.id) \
            .order_by('date_created') \
            .values('coin_amount').first()

        if bundle:
            description = "Poin dari Try Out %s" % packet.label
            coin_amount = bundle['coin_amount']
            amount = coin_amount * 0.2
            caused_content_type = ContentType.objects \
                .get_for_model(instance, for_concrete_model=False)

            Points.objects.create(
                caused_object_id=instance.id, caused_content_type=caused_content_type,
                user=instance.user, transaction_type=IN, amount=amount,
                description=description)

        return instance
