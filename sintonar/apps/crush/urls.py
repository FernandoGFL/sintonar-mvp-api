from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sintonar.apps.crush.views.crush import CrushViewSet, UserCrushViewSet

router = DefaultRouter()
router.register('users', UserCrushViewSet, basename='user_crush')
router.register('', CrushViewSet, basename='crush')


urlpatterns = [
    path('', include(router.urls)),
]
