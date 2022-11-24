from crushonu.apps.utils.serializers.fields import CustomChoiceField
from crushonu.apps.authentication.models import (
    User,
    UserConfirm
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
        allow_null=False
    )
    preference = CustomChoiceField(
        choices=User.PREFERENCES,
        allow_blank=False,
        allow_null=False
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
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
