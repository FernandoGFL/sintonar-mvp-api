from crushonu.apps.utils.serializers.fields import CustomChoiceField
from crushonu.apps.authentication.models import (
    User,
    UserConfirm,
    UserPhoto
)

from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from PIL import Image
from io import BytesIO


def resize_image(image):
    # Pega a extensão do arquivo
    extension = image.name.split('.')[-1].upper()

    if extension == 'JPG':
        extension = 'JPEG'

    # Carrega a imagem com o PIL
    img = Image.open(image)
    img.convert('RGB')

    # Redimensiona a imagem
    img.thumbnail((640, 800))

    # Comprime a imagem
    img_io = BytesIO()
    img.save(img_io, format=extension, optimize=True, quality=60)
    img_io.seek(0)

    file_name = image.name

    resized_file = InMemoryUploadedFile(
        img_io, None, file_name, f'image/{file_name.split(".")[-1]}',
        img_io.tell, None
    )

    return resized_file


class JWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_confirmed:
            raise PermissionDenied(
                "Esse usuário ainda não confirmou seu email",
                "not_confirmed",
            )

        data['has_description'] = self.user.has_description
        data['has_uploaded_photo'] = self.user.has_uploaded_photo

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email já cadastrado"
            )
        ]
    )
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
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )

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


class UserPhotoSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source='photos', read_only=True)

    class Meta:
        model = UserPhoto
        fields = (
            "id",
            "photos",
            "url",
            "is_favorite",
        )
        extra_kwargs = {
            "photos": {"write_only": True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['photos'].read_only = True

    def validate_is_favorite(self, value):
        if value is False and UserPhoto.objects.filter(
            user=self.context['request'].user
        ).exists() is False:
            value = True

        return value

    def validate(self, attrs):
        # Verificar se a imagem tem mais de 10MB
        if attrs['photos'].size > 1024 * 1024 * 10:
            raise serializers.ValidationError(
                {"detail": "A imagem não pode ter mais de 10MB"})

        return super().validate(attrs)

    def create(self, validated_data):
        if self.context['request'].user.userphoto_set.count() >= 3:
            raise serializers.ValidationError(
                {"detail": "Limite de fotos atingido"})

        photo = resize_image(validated_data['photos'])

        user_photo = UserPhoto.objects.create(
            user=self.context['request'].user,
            photos=photo,
            is_favorite=validated_data.get('is_favorite', False)
        )

        return user_photo

    def update(self, instance, validated_data):
        if validated_data.get('is_favorite', False):
            UserPhoto.objects.filter(
                user=instance.user).update(is_favorite=False)

        return super().update(instance, validated_data)


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
            "has_description",
            "has_uploaded_photo",
        )
        read_only_fields = (
            'id',
            'email',
            'photos',
            'has_description',
            'has_uploaded_photo',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['photos'] = UserPhotoSerializer(
            instance.userphoto_set.all().order_by('-is_favorite'),
            many=True
        ).data

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'description' in validated_data and instance.has_description is False:
            instance.has_description = True

        return super().update(instance, validated_data)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "password",
            "new_password",
        )

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['password']):
            raise serializers.ValidationError(
                {"detail": "Senha atual incorreta"})

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance
