from django.contrib.auth import get_user_model
from rest_framework import serializers

from sintonar.apps.authentication.serializers.authentication import UserPhotoSerializer
from sintonar.apps.authentication.serializers.fields.user import UserField
from sintonar.apps.crush.models.crush import Crush
from sintonar.apps.utils.serializers.fields import CustomChoiceField

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

    def create(self, validated_data) -> Crush:
        user_from = validated_data.pop('user_from')
        user_to = validated_data.pop('user_to')
        kiss = validated_data.pop('kiss')

        crush = Crush.objects.filter(
            user_from=user_from,
            user_to=user_to,
        ).first()

        if crush:
            crush.kiss = kiss
            crush.save()

        else:
            crush = Crush.objects.create(
                user_from=user_from,
                user_to=user_to,
                kiss=kiss,
            )

        if crush.kiss:
            crush_kissed = Crush.objects.filter(
                user_to=user_from,
                user_from=user_to,
                kiss=True,
            )

            if crush_kissed.exists():
                crush_kissed.update(match=True)

                crush.match = True
            else:
                crush.match = False

        else:
            Crush.objects.filter(
                user_to=user_from,
                user_from=user_to,
                kiss=True,
            ).update(match=False)

            crush.match = False

        crush.save()

        return crush

    def to_representation(self, instance) -> dict:
        serializer = CrushDisplaySerializer(instance, context=self.context)

        return serializer.data


class UserCrushDisplaySerializer(serializers.ModelSerializer):
    gender = CustomChoiceField(choices=User.GENDER)
    full_name = serializers.CharField()
    age = serializers.IntegerField()

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
            instance.userphoto_set.all(),
            many=True
        ).data

        return data


class CrushDisplaySerializer(serializers.ModelSerializer):
    user = UserCrushDisplaySerializer(source='user_from')

    class Meta:
        model = Crush
        fields = (
            'id',
            'user',
            'match',
        )
