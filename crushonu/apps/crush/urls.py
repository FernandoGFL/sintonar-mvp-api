from crushonu.apps.crush.views.crush import (
    CrushViewSet,
    UserCrushViewSet,
    CrushListSentKissesViewSet
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('', CrushViewSet, basename='crush')
router.register('sent-kisses', CrushListSentKissesViewSet,
                basename='sent_kisses')
router.register('users', UserCrushViewSet, basename='user_crush')


urlpatterns = [
    path('', include(router.urls)),
]
