from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.decorators import action

from WAKe_server.settings import KAKAO_REST_API_KEY, KAKAO_CALLBACK_URI


class LoginViewSet(viewsets.GenericViewSet):

    @action(detail=False, methods=['GET'])
    def kakao(self, request, *args, **kwargs):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(f"{kakao_api}&client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}")