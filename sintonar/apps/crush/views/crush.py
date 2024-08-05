from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sintonar.apps.authentication.models import User, UserPhoto
from sintonar.apps.crush.models.crush import Crush
from sintonar.apps.crush.serializers.crush import (
    CrushCreateSerializer,
    CrushDisplaySerializer,
    UserCrushDisplaySerializer,
)


class UserCrushViewSet(GenericViewSet,
                       ListAPIView,
                       ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserCrushDisplaySerializer
    permission_classes = (IsAuthenticated,)

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

        return queryset.filter(
            query
        ).exclude(
            id=self.request.user.id
        ).exclude(
            id__in=crushs
        ).order_by('date_joined')


class CrushViewSet(GenericViewSet,
                   ListModelMixin,
                   CreateModelMixin,
                   RetrieveModelMixin):
    queryset = Crush.objects.all()
    serializer_class = CrushCreateSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CrushDisplaySerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        users_with_photos = UserPhoto.objects.values_list('user_id').distinct()

        query = Q(
            kiss=True,
            user_to=self.request.user,
            user_from__id__in=users_with_photos,
        )

        if self.action == 'list':
            matched = query_params.get('matched', 'false') in ('true', 'True',)

            if matched:
                query &= Q(match=True)
            else:
                query &= Q(match=False)

        return queryset.filter(
            query,
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not UserPhoto.objects.filter(user=request.user).exists():
            raise ValidationError(
                detail={
                    'detail': _('You need to upload at least one photo to send a crush.')
                }
            )

        data = dict(**request.data)
        data['user_from'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='matched',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by matched crushs.',
                examples=[
                    OpenApiExample(
                        name='Matched',
                        summary='If you want to filter by matched crushs.',
                        value='true',
                    )
                ]
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
