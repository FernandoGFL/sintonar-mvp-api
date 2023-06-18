from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

from crushonu.apps.authentication.serializers.authentication import JWTSerializer
from crushonu.apps.authentication.views.authentication import (
    UserRegisterViewSet,
    UserConfirmView,
    UserResendConfirmView,
    UserViewSet,
    UserPhotoViewSet,
    UserChangePasswordView
)
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

# JWT Auth
urlpatterns = [
    path(
        'password-reset/',
        include(
            'django_rest_passwordreset.urls',
            namespace='password_reset'
        )
    ),
    path(
        'token/',
        TokenObtainPairView.as_view(serializer_class=JWTSerializer),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(serializer_class=TokenRefreshSerializer),
        name='token_refresh'
    ),
    path(
        'register/',
        UserRegisterViewSet.as_view({'post': 'create'}),
        name='register_user'
    ),
    path(
        'confirm/<uuid:uuid>/',
        UserConfirmView.as_view(),
        name='confirm_user'
    ),
    path(
        'resend-confirm/',
        UserResendConfirmView.as_view(),
        name='resend_confirm_user'
    ),
    path(
        'me/',
        UserViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update'
            }
        ),
        name='user-detail'
    ),
    path(
        'me/photos/',
        UserPhotoViewSet.as_view(
            {
                'post': 'create',
                'get': 'list'
            }
        ),
        name='userphoto-list'
    ),
    path(
        'me/photos/<uuid:pk>/',
        UserPhotoViewSet.as_view(
            {
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update'
            }
        ),
        name='userphoto-detail'),
    path(
        'change-password/',
        UserChangePasswordView.as_view(),
        name='change_password_user'
    )
]
