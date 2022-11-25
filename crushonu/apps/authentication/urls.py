from django.urls import path

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
    UserPhotoViewSet
)

# JWT Auth
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(serializer_class=JWTSerializer),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('register/',
         UserRegisterViewSet.as_view({'post': 'create'}), name='register_user'),
    path('user-confirm/<uuid:uuid>/',
         UserConfirmView.as_view(), name='user_confirm'),
    path('user-resend-confirm/',  UserResendConfirmView.as_view(),
         name='user_resend_confirm'),
    path('user/', UserViewSet.as_view({'get': 'retrieve',
         'put': 'update', 'patch': 'partial_update'}), name='user_detail'),
    path('user/photos/', UserPhotoViewSet.as_view(
        {'post': 'create', 'get': 'list'}), name='user_photo_list'),
    path('user/photos/<int:pk>/', UserPhotoViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='user_photo_detail'),
]
