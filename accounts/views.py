from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from requests import Request
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import SlidingToken

from accounts.serializers import LogoutSerializer


class KaKaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/social/kakao/login/callback/"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        print(request.POST)
        return super().post(request, *args, **kwargs)
