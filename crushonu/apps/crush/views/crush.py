from crushonu.apps.crush.serializers.crush import (
    UserCrushDisplaySerializer,
    CrushCreateSerializer,
    CrushDisplaySerializer
)
from crushonu.apps.crush.models.crush import Crush
from crushonu.apps.authentication.models import (
    User,
    UserPhoto
)

from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin
)
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.viewsets import (
    GenericViewSet,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Q


class UserCrushViewSet(GenericViewSet,
                       ListAPIView,
                       ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserCrushDisplaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        users_with_photos = UserPhoto.objects.values_list('user_id').distinct()

        query = Q(
            is_confirmed=True,
            id__in=users_with_photos,
        )

        preference = self.request.user.preference
        gender = self.request.user.gender

        if preference == User.WOMAN:
            query &= Q(gender=User.WOMAN) | Q(gender=User.NEUTRAL)

        elif preference == User.MAN:
            query &= Q(gender=User.MAN) | Q(gender=User.NEUTRAL)

        if gender == User.MAN:
            query &= Q(preference=User.MAN) | Q(preference=User.ALL)

        elif gender == User.WOMAN:
            query &= Q(preference=User.WOMAN) | Q(preference=User.ALL)

        crushs = Crush.objects.filter(
            user_from=self.request.user,
        ).values_list('user_to')

        return queryset.filter(query).exclude(id=self.request.user.id).exclude(id__in=crushs).order_by('date_joined')


class CrushViewSet(GenericViewSet,
                   ListModelMixin,
                   CreateModelMixin):
    queryset = Crush.objects.all()
    serializer_class = CrushCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CrushCreateSerializer
        elif self.action == 'list':
            return CrushDisplaySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(
            user_to=self.request.user,
            kiss=True,
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not UserPhoto.objects.filter(user=request.user).exists():
            return Response(
                {"message": "Você precisa adicionar uma foto para participar do jogo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = dict(**request.data)
        data['user_from'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
