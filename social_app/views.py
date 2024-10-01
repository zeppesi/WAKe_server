import datetime
import random

import requests
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import SlidingToken

from WAKe_server.settings import KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, KAKAO_CALLBACK_URI, LOGIN_REDIRECT_URL, \
    KAKAO_ADMIN_KEY, BASE_URL
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from accounts.models import User, CommonProfile
from accounts.serializers import UserSerializer, LogoutSerializer, KakaoCallbackSerializer
from accounts.utils import token_serializer

KAKAO_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_API = "https://kapi.kakao.com/v2/user/me"


class KaKaoLoginViewSet(viewsets.GenericViewSet):
    serializer_class = KakaoCallbackSerializer
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client

    @action(detail=False, methods=['GET'])
    def getcode(self, request: Request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(f"{kakao_api}&client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}")

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated], serializer_class=LogoutSerializer)
    def resign(self, request: Request):
        user = request.user

        # todo: 일단 kakao만 구현했으므로
        kakao_uid = user.socialaccount_set.filter(provider='kakao').first().uid
        # kakao_uid = 3664195039
        requests.post(
            url="https://kapi.kakao.com/v1/user/unlink",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}",
            },
            data={
                "target_id_type": "user_id",
                "target_id": int(kakao_uid)
            }
        )
        user.socialaccount_set.all().delete()

        token_str = request.META.get('HTTP_AUTHORIZATION', '').split()[1]
        token = SlidingToken(token_str)
        token.blacklist()

        return Response(dict(message='logout succeeded'))

    @action(detail=False, methods=['GET'], serializer_class=KakaoCallbackSerializer)
    def callback(self, request: Request):
        code = request.GET["code"]

        if not code:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # kakao에 access token 발급 요청
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": KAKAO_CALLBACK_URI,
            "code": code,
            "client_secret": KAKAO_CLIENT_SECRET
        }
        headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8"}
        token = requests.post(KAKAO_TOKEN_API, data=data, headers=headers).json()  # 받은 코드로 구글에 access token 요청하기
        access_token = token['access_token']  # 받은 access token
        if not access_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # kakao에 user info 요청
        headers = {"Authorization": f"Bearer ${access_token}"}
        user_information = requests.get(KAKAO_USER_API, headers=headers).json()  # 받은 access token 으로 user 정보 요청

        kakao_account = user_information.get('kakao_account')
        email = kakao_account.get('email')
        nickname = kakao_account.get('profile').get('nickname')

        # 유저가 이미 디비에 있는지 확인
        try:
            # a. 있으면 토큰 발행
            user = User.objects.get(email=email)
            token = token_serializer(user)
            access_token = token['access']
            refresh_token = token['refresh']
            res = redirect(LOGIN_REDIRECT_URL+f'?access={access_token}&refresh={refresh_token}')
            res.set_cookie(
                'access',
                access_token,
                max_age=3600 * 24 * 3,
                domain='.zps.kr',
                secure=True,
                httponly=True,
                samesite=False,
            )
            res.set_cookie(
                'refresh',
                refresh_token,
                max_age=3600 * 24 * 3,
                domain='.zps.kr',
                secure=True,
                httponly=True,
                samesite=False,
            )
            return res

        except User.DoesNotExist:
            # b. 없으면 유저 및 프로필 생성
            data = {"access_token": access_token, "code": code}
            accept = requests.post(f"{BASE_URL}social/kakao/login/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)

            timestamp = int(datetime.datetime.now().timestamp())
            password = str(random.randint(0, timestamp))

            user = User.objects.get(email=email)
            profile = CommonProfile.objects.create(user=user, name=nickname)

            try:
                user = User.objects.get(email=email)
                token = token_serializer(user)
                access_token = token['access']
                refresh_token = token['refresh']
                res = redirect(LOGIN_REDIRECT_URL+f'?access={access_token}&refresh={refresh_token}')
                res.set_cookie(
                    'access',
                    access_token,
                    max_age=3600 * 24 * 3,
                    domain='.zps.kr',
                    secure=True,
                    httponly=True,
                    samesite=False,
                )
                res.set_cookie(
                    'refresh',
                    refresh_token,
                    max_age=3600 * 24 * 3,
                    domain='.zps.kr',
                    secure=True,
                    httponly=True,
                    samesite=False,
                )
                return res
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class KaKaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/social/kakao/callback/"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        print(request.POST)
        return super().post(request, *args, **kwargs)
