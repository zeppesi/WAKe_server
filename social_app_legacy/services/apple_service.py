import json
from typing import Union
import requests
from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from allauth.socialaccount.providers.apple.provider import AppleProvider
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

from accounts.models import User
from dtos import OauthStateInputDTO
from social_app_legacy.services.base_service import BaseSocialLoginService
from WAKe_server.settings import SOCIALACCOUNT_PROVIDERS


class AppleLoginService(BaseSocialLoginService):
    adapter_class = AppleOAuth2Adapter
    provider_class = AppleProvider

    def __init__(self, state: Union[OauthStateInputDTO] = None, **kwargs):
        super().__init__(**kwargs)
        self.state: OauthStateInputDTO = state

    def handle_callback(self):
        try:
            super().handle_callback()
        except self.DuplicatedEmailError as e:
            # 원래는 안해도 되지만, 기존에 user resign에서 apple revoke 기능을 처리하지 않은 유저의 경우가 존재함.
            # 이 경우, 애플 로그인을 다시 하려고 할 때 email 정보가 없는 경우가 발생함.
            # 이 경우 revoke를 해야함.
            # https://github.com/invertase/react-native-apple-authentication#faqs 의 1번 항목
            # Why does full name and email return null?
            # 23.7.14 raise e 해줘서 duplicated 에러 처리 되도록 해야함.
            self.revoke_apple_token_by_user_data(self.token.user_data)
            raise e

    @classmethod
    def revoke_apple_token(cls, user: User):
        social_account = user.socialaccount_set.filter(provider='apple').last()
        if social_account is not None:
            extra_data = social_account.extra_data
            if extra_data is not None:
                cls.revoke_apple_token_by_user_data(extra_data)

    @classmethod
    def revoke_apple_token_by_user_data(cls, extra_data):
        if extra_data is not None:
            client_id = extra_data.get('aud')
            secret = SOCIALACCOUNT_PROVIDERS['apple']['APP']['secret']
            client_secret = AppleOAuth2Client(None, client_id, secret, None, None, None, []).generate_client_secret()
            requests.post(
                'https://appleid.apple.com/auth/revoke',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'token': extra_data.get('refresh_token')
                }
            )
