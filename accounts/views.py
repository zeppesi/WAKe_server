import datetime
import random

import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import SlidingToken

from WAKe_server.settings import KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, KAKAO_CALLBACK_URI
from accounts.models import User, CommonProfile
from accounts.serializers import UserSerializer, LogoutSerializer, KakaoCallbackSerializer
from accounts.utils import token_serializer

KAKAO_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_API = "https://kapi.kakao.com/v2/user/me"


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated], serializer_class=LogoutSerializer)
    def logout(self, request: Request):
        token_str = request.META.get('HTTP_AUTHORIZATION', '').split()[1]
        token = SlidingToken(token_str)
        token.blacklist()
        return Response(dict(message='logout succeeded'))


class KaKaoLoginViewSet(viewsets.GenericViewSet):

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
        user_infomation = requests.get(KAKAO_USER_API, headers=headers).json()  # 받은 access token 으로 user 정보 요청

        kakao_account = user_infomation.get('kakao_account')
        email = kakao_account.get('email')

        # 유저가 이미 디비에 있는지 확인
        try:
            # a. 있으면 토큰 발행
            user = User.objects.get(email=email)
            token = token_serializer(user)
            return Response(dict(token=token))

        except User.DoesNotExist:
            # b. 없으면 유저 및 프로필 생성
            timestamp = int(datetime.datetime.now().timestamp())
            password = str(random.randint(0, timestamp))
            user = User.objects.create_user(email, password)
            profile = CommonProfile.objects.create(user=user, name=email)

            try:
                user = User.objects.get(email=email)
                token = token_serializer(user)
                return Response(dict(token=token))
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
