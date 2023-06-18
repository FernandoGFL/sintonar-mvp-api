from rest_framework.serializers import (
    RelatedField,
    ValidationError
)

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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
                _(f'Invalid pk \"{data}\" - object does not exist.')
            )
