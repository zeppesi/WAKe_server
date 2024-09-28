from django.urls import path, include
from rest_framework.routers import SimpleRouter

from accounts.views import KaKaoLoginView

app_name = 'accounts'

router = SimpleRouter()
# router.register('kakao', KaKaoLoginView, basename='kakao')
# router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("", include("dj_rest_auth.registration.urls")),
    path(
        "kakao/login/",
        KaKaoLoginView.as_view(),
        name="api_accounts_kakao_oauth",
    )
]
