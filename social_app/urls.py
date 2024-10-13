from django.urls import path, include
from rest_framework.routers import SimpleRouter

from social_app.views import KaKaoLoginViewSet, KaKaoLogin

app_name = 'social'

router = SimpleRouter()
router.register('kakao', KaKaoLoginViewSet, basename='kakao_callback')
# router.register('apple', AppleLoginViewSet, basename='apple')

urlpatterns = [
    path('', include((router.urls, 'social'))),
    path(
        "kakao/login/",
        KaKaoLogin.as_view(),
        name="api_accounts_kakao_oauth",
    )
]
