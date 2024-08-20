import json
from typing import Union

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter

from WAKe_server.settings import KAKAO_ADMIN

from accounts.models import User
from dtos import OauthStateInputDTO
from social_app.services.base_service import BaseSocialLoginService


class KakaoLoginService(BaseSocialLoginService):
    adapter_class = KakaoOAuth2Adapter
    provider_class = KakaoProvider

    def __init__(self, state: Union[OauthStateInputDTO] = None, **kwargs):
        super().__init__(**kwargs)
        self.state: OauthStateInputDTO = state

    def handle_callback(self):
        super().handle_callback()

    def check_channel_relation(self):
        """
        아래에 False를 명시한 이유는 나중에 기획이 바뀌어
        단순히 True, False가 아닌 channel relation의 상태에 따라 처리할 수도 있기 때문에
        명시함
        """
        user: User = self.request.user
        channel_relation = False

        social_account: SocialAccount = user.socialaccount_set.filter(provider='kakao').last()
        if social_account is None:
            channel_relation = False
        else:
            res = requests.get(
                'https://kapi.kakao.com/v1/api/talk/channels',
                params=dict(target_id_type='user_id', target_id=social_account.uid),
                headers={
                    'Authorization': f'KakaoAK {KAKAO_ADMIN}',
                    'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
                }
            )
            channels = res.json().get('channels')
            if channels is None or len(channels) == 0:
                if res.json().get('code') == -402:
                    channel_relation = False
                else:
                    channel_relation = False

            if channels[0].get('relation') == 'ADDED':
                channel_relation = True

        output_dto = dict(
            state=channel_relation
        )

        return output_dto
