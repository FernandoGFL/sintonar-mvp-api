from crushonu.apps.authentication.serializers.authentication import (
    UserRegisterSerializer,
    UserSerializer,
    UserPhotoSerializer
)
from crushonu.apps.authentication.models import (
    UserConfirm,
    User,
    UserPhoto
)
from crushonu.apps.authentication.signals import send_email_confirmation

from django.db import transaction

from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
)
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
                {"detail": "Código de confirmação inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Usuário confirmado com sucesso."},
            status=status.HTTP_200_OK
        )


class UserResendConfirmView(APIView):
    def post(self, request, format=None):
        email = request.data.get("email", None)

        if not email:
            return Response(
                {"detail": "Email não informado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)

            if user.is_confirmed:
                return Response(
                    {"message": "Usuário já confirmado."},
                    status=status.HTTP_200_OK,
                )

            user_confirm = UserConfirm.objects.get(user=user)
            send_email_confirmation(
                sender=UserConfirm,
                instance=user_confirm,
                created=True,
            )

        except User.DoesNotExist:
            pass

        return Response(
            {"message": "Email de confirmação reenviado com sucesso."},
            status=status.HTTP_200_OK
        )


class UserViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet,
    GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class UserPhotoViewSet(ModelViewSet):
    queryset = UserPhoto.objects.all()
    serializer_class = UserPhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPhoto.objects.filter(
            user=self.request.user
        ).order_by(
            "-is_favorite",
            "updated_at"
        )

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        if not self.request.user.has_uploaded_photo:
            self.request.user.has_uploaded_photo = True
            self.request.user.save()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class UserIsConfirmedView(APIView):
    def get(self, request, format=None):
        try:
            user = User.objects.get(email=request.query_params.get("email"))

        except User.DoesNotExist:
            return Response(
                {"detail": "Usuário não encontrado."},
            )

        return Response(
            {"is_confirmed": user.is_confirmed},
            status=status.HTTP_200_OK
        )


class TemporaryDeleteUserView(APIView):
    def delete(self, request, format=None):
        try:
            user = User.objects.get(email=request.data.get("email"))

        except User.DoesNotExist:
            return Response(
                {"detail": "Usuário não encontrado."},
            )

        user.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
