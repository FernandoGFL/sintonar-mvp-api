from crushonu.apps.authentication.serializers.authentication import UserRegisterSerializer
from crushonu.apps.authentication.models import UserConfirm

from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
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


class UserConfirmView(APIView):
    def post(self, request, uuid, format=None):
        try:
            user_confirm = UserConfirm.objects.get(identification_code=uuid)

            user = user_confirm.user

            if user.is_confirmed:
                return Response(
                    {"message": "Usuário já confirmado."},
                    status=status.HTTP_200_OK,
                )

            user.is_confirmed = True
            user.save()

        except UserConfirm.DoesNotExist:
            return Response(
                {"message": "Código de confirmação inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Usuário confirmado com sucesso."},
            status=status.HTTP_200_OK
        )
