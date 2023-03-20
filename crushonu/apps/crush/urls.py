from crushonu.apps.crush.views.crush import (
    CrushViewSet,
    UserCrushViewSet,
)

from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('users', UserCrushViewSet, basename='user_crush')
router.register('', CrushViewSet, basename='crush')


urlpatterns = [
    path('', include(router.urls)),
]
