from django.urls import path, include
from rest_framework.routers import SimpleRouter

from social_app.views import KaKaoLoginViewSet, AppleLoginViewSet

app_name = 'social'

router = SimpleRouter()
router.register('kakao', KaKaoLoginViewSet, basename='kakao')
router.register('apple', AppleLoginViewSet, basename='apple')

urlpatterns = [
    path('', include((router.urls, 'social')))
]
