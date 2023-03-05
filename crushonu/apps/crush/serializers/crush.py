from crushonu.apps.authentication.serializers.fields.user import UserField
from crushonu.apps.authentication.serializers.authentication import UserPhotoSerializer
from crushonu.apps.crush.models.crush import Crush
from crushonu.apps.utils.serializers.fields import CustomChoiceField

from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class CrushCreateSerializer(serializers.ModelSerializer):
    user_from = UserField()
    user_to = UserField()

    class Meta:
        model = Crush
        fields = (
            'id',
            'user_from',
            'user_to',
            'kiss',
            'created_at',
            'updated_at',
        )

    def create(self, validated_data):
        user_from = validated_data.pop('user_from')
        user_to = validated_data.pop('user_to')
        kiss = validated_data.pop('kiss')

        crush = Crush.objects.filter(
            user_from=user_from,
            user_to=user_to,
        ).first()

        if crush:
            crush.kiss = kiss

        else:
            crush = Crush.objects.create(
                user_from=user_from,
                user_to=user_to,
                kiss=kiss,
            )

        if kiss is True:
            try:
                crush_kissed = Crush.objects.get(
                    user_to=user_from,
                    user_from=user_to,
                    kiss=True,
                )
                crush_kissed.match = True
                crush_kissed.save()

                crush.match = True

            except Crush.DoesNotExist:
                crush.match = False
        else:
            crush.match = False

        crush.save()

        return crush

    def to_representation(self, instance):
        serializer = CrushDisplaySerializer(instance)

        return serializer.data


class UserCrushDisplaySerializer(serializers.ModelSerializer):
    gender = CustomChoiceField(choices=User.GENDER)

    class Meta:
        model = User
        fields = (
            'id',
            'full_name',
            'age',
            'gender',
            'description',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['photos'] = UserPhotoSerializer(
            instance.userphoto_set.all(), many=True).data

        return data


class CrushDisplaySerializer(serializers.ModelSerializer):
    user_from = UserCrushDisplaySerializer()
    user_to = UserCrushDisplaySerializer()

    class Meta:
        model = Crush
        fields = (
            'id',
            'user_from',
            'user_to',
            'match',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.user_to == self.context['request'].user:
            data['kissed'] = Crush.objects.filter(
                user_from=instance.user_to, user_to=instance.user_from
            ).exists()

        return data
