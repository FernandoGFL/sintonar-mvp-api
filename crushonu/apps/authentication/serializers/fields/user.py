from rest_framework.serializers import (
    RelatedField,
    ValidationError
)

from django.contrib.auth import get_user_model


User = get_user_model()


class UserField(RelatedField):
    def get_queryset(self):
        return User.objects.filter(
            is_confirmed=True
        )

    def to_internal_value(self, data):
        try:
            return User.objects.get(
                id=data,
                is_confirmed=True,
            )
        except User.DoesNotExist:
            raise ValidationError(
                f'Pk inválido \"{data}\" - objeto não existe.'
            )
