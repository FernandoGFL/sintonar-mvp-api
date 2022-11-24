from crushonu.apps.authentication.serializers.authentication import UserRegisterSerializer

from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status


class UserRegisterViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {
            "message": "Usuário criado com sucesso, verifique seu email para confirmar sua conta.",
        }

        return Response(
            data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
