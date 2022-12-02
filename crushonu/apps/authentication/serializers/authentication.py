from crushonu.apps.utils.serializers.fields import CustomChoiceField
from crushonu.apps.authentication.models import (
    User,
    UserConfirm,
    UserPhoto
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers


class JWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_confirmed:
            raise AuthenticationFailed(
                "Esse usuário ainda não confirmou seu email",
                "not_confirmed",
            )

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    gender = CustomChoiceField(
        choices=User.GENDER,
        allow_blank=False,
        allow_null=False,
        required=True,
    )
    preference = CustomChoiceField(
        choices=User.PREFERENCES,
        allow_blank=False,
        allow_null=False,
        required=True,
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "birthday",
            "first_name",
            "last_name",
            "gender",
            "preference",
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data,
        )

        UserConfirm.objects.create(user=user)

        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já cadastrado")

        return value


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = (
            "id",
            "photo",
        )

    def create(self, validated_data):
        if self.context['request'].user.userphoto_set.count() >= 5:
            raise serializers.ValidationError("Limite de fotos atingido")

        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    gender = CustomChoiceField(
        choices=User.GENDER,
        allow_blank=False,
        allow_null=False,
        required=False
    )
    preference = CustomChoiceField(
        choices=User.PREFERENCES,
        allow_blank=False,
        allow_null=False,
        required=False
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "birthday",
            "first_name",
            "last_name",
            "description",
            "gender",
            "preference",
            "full_name",
            "age",
        )
        read_only_fields = (
            'id',
            'email',
            'photos'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['photos'] = UserPhotoSerializer(
            instance.userphoto_set.all(), many=True).data

        return data
