import json

from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from core.utils.time import TimeManager
from dtos import OauthStateInputDTO, DTOResponseFormatter
from social_app.serializers.base_serializer import SocialLoginSerializer
from social_app.services.apple_service import AppleLoginService
from social_app.services.kakao_service import KakaoLoginService


class LoginViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    adapter_class = None

    def get_serializer_context(self):
        context = super(LoginViewSet, self).get_serializer_context()
        context['nested'] = self.request.META.get('HTTP_NESTED', 'true')
        return context

    @action(detail=False, methods=['POST'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        new_user: bool = data['new_user']
        user: User = data['user']
        response_status = status.HTTP_200_OK
        if new_user or not hasattr(user, 'common_profile'):
            user = serializer.create(serializer.validated_data)
            response_status = status.HTTP_201_CREATED

        if not user.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user.last_login = TimeManager.now()
        user.save()

        token, new_user = self.token_model.objects.get_or_create(user=user)

        if request.data.get('state'):
            redirect_url = request.data.get('state')
            if '?' in redirect_url:
                redirect_url += f'&token={token.key}&new_user={new_user}'
            else:
                redirect_url += f'?token={token.key}&new_user={new_user}'
            return redirect(redirect_url)

        return Response(dict(key=token.key, new_user=new_user), status=response_status)

    @action(detail=False, methods=['GET'])
    def callback(self, request):
        return Response(status=status.HTTP_200_OK)


class KaKaoLoginViewSet(LoginViewSet):
    adapter_class = KakaoOAuth2Adapter
    permission_classes = [AllowAny]

    @action(detail=False, methods=['POST'], serializer_class=SocialLoginSerializer)
    def login(self, request):
        user = request.user
        service = KakaoLoginService(
            request=request,
            user=user,
            access_token=request.data.get('access_token'),
            refresh_token=request.data.get('refresh_token'),
        )
        try:
            service.handle_login()
        except service.DuplicatedEmailError as e:
            return Response(DTOResponseFormatter.run(errors=e.message), status=status.HTTP_400_BAD_REQUEST)
        output_dto = service.token_serializer()
        return Response(DTOResponseFormatter.run(output_dto))

    @action(detail=False, methods=['GET'])
    def callback(self, request):
        state = request.query_params.get('state')
        authorization_code = request.query_params.get('code')

        state = json.loads(state)
        state_input_dto = OauthStateInputDTO(**state)

        service = KakaoLoginService(request=request, state=state_input_dto, authorization_code=authorization_code)

        try:
            service.handle_callback()
        except service.SocialLoginError as e:
            print(e)
            redirect_url = service.redirect_url_with_error(state_input_dto.redirect)
            return redirect(
                redirect_url,
                e.message,
            )
        except service.DuplicatedEmailError as e:
            redirect_url = service.redirect_url_with_error(
                state_input_dto.redirect,
                e.message
            )
            return redirect(redirect_url)
        except Exception as e:
            print(e)
            redirect_url = service.redirect_url_with_error(
                state_input_dto.redirect
            )
            return redirect(redirect_url)
        redirect_url = service.redirect_url_with_token(state_input_dto.redirect)
        return redirect(redirect_url)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def check_relation(self, request):
        service = KakaoLoginService(request=request, )
        output_dto = service.check_channel_relation()
        return Response(DTOResponseFormatter.run(output_dto))


class AppleLoginViewSet(LoginViewSet):
    adapter_class = AppleOAuth2Adapter
    permission_classes = [AllowAny]

    @action(detail=False, methods=['POST'], serializer_class=SocialLoginSerializer)
    def login(self, request):
        user = request.user
        authorization_code = request.data.get('code')
        service = AppleLoginService(request=request, authorization_code=authorization_code, user=user)
        try:
            service.handle_callback()
            output_dto = service.token_serializer()
        except service.DuplicatedEmailError as e:
            return Response(DTOResponseFormatter.run(errors=e.message), status=status.HTTP_400_BAD_REQUEST)
        return Response(DTOResponseFormatter.run(output_dto))

    @action(detail=False, methods=['POST'], serializer_class=SocialLoginSerializer)
    def callback(self, request):
        state = request.data.get('state') or request.query_params.get('state')
        if state is None:
            return redirect('https://www.wake.zps.kr/')
        state = '{' + state + '}'
        state = json.loads(state)
        state_input_dto = OauthStateInputDTO(**state)

        authorization_code = request.data.get('code') or request.query_params.get('code')

        service = AppleLoginService(request=request, state=state_input_dto, authorization_code=authorization_code)
        try:
            service.handle_callback()
        except service.SocialLoginError as e:
            print(e)
            redirect_url = service.redirect_url_with_error(state_input_dto.redirect)
            return redirect(redirect_url)
        except service.DuplicatedEmailError as e:
            redirect_url = service.redirect_url_with_error(
                state_input_dto.redirect,
                e.message
            )
            return redirect(redirect_url)
        except Exception as e:
            print(e)
            redirect_url = service.redirect_url_with_error(state_input_dto.redirect)
            return redirect(redirect_url)

        redirect_url = service.redirect_url_with_token(state_input_dto.redirect)
        return redirect(redirect_url)
