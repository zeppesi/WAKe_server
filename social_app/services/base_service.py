from typing import Optional

from allauth.socialaccount.adapter import get_adapter, DefaultSocialAccountAdapter
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp, SocialToken, SocialLogin, SocialAccount
from allauth.socialaccount.providers.base import Provider
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from allauth.utils import build_absolute_uri
from django.urls import reverse
from requests import HTTPError
from rest_framework_simplejwt.tokens import SlidingToken

from accounts.models import User
from dtos import OauthStateInputDTO


class BaseSocialLoginService:
    adapter_class = None
    request = None
    state: Optional[OauthStateInputDTO] = None
    login: Optional[SocialLogin] = None

    class SocialLoginError(Exception):
        def __init__(self, message):
            self.message = message

    class UserDoesNotExists(Exception):
        def __init__(self, message):
            self.message = message

    class DuplicatedEmailError(Exception):
        def __init__(self, message: Optional[dict] = None):
            self.message = message

    def __init__(
            self,
            request,
            user=None,
            access_token=None,
            refresh_token=None,
            authorization_code=None,
    ):
        self.request = request
        self._user = user
        self.authorization_code = authorization_code
        if access_token is not None:
            token = SocialToken(token=access_token, token_secret=refresh_token)
            token.app = self.social_app
            self._token = token
        self._is_new = False

    def handle_login(self):
        # 해당 함수 오버라이드 하여 우리 프로필 등의 데이터 저장시 사용
        # access token이 있는 경우
        try:
            self.complete_login()
            self.check_new_user()
            complete_social_login(self.request, self.login)
            self.already_signup_user()
            self.check_user()
        except HTTPError as e:
            raise self.SocialLoginError(dict(login=self.adapter.provider_id))

    def check_new_user(self):
        # 해당 유저가 기존 유저인지 신규유저인지 확인
        try:
            User.objects.get(email=self.login.user.email)
            self._is_new = False
        except User.DoesNotExist:
            self._is_new = True

    def handle_callback(self):
        # 인가코드가 있는 경우
        self.get_access_token()
        self.handle_login()

    def get_social_login(self, adapter, app, token, response, nickname):
        pass

    def get_callback_url(self):
        callback_url = reverse(f'social:social:{self.social_app.provider}-callback')
        return build_absolute_uri(self.request, callback_url)

    def get_access_token(self) -> SocialToken:
        """
        인가 코드로 access token 받기
        """
        app = self.social_app
        client = self.get_client(self.request, app)

        try:
            access_token_data = client.get_access_token(self.authorization_code)
            token = self.adapter.parse_token(access_token_data)
            token.app = app
            self._token = token
        except OAuth2Error as e:
            raise Exception(e)
        return token

    def complete_login(self):
        # 아직 save하지 않음
        social_login: SocialLogin = self.adapter.complete_login(self.request, self.social_app, self.token)
        if getattr(self.state, 'jwt_token', None) is not None:
            # 기존 임의의 이메일을 가진 유저와 연결함
            try:
                user = self.get_user_by_jwt_token(self.state.jwt_token)
            except User.DoesNotExist:
                raise self.SocialLoginError(dict(login=self.adapter.provider_id))
            user.email = social_login.user.email
            social_login.user = user
        social_login.token = self.token
        self.login = social_login
        return social_login

    def already_signup_user(self):
        account = self.login.account
        try:
            user = account.user
        except SocialAccount.user.RelatedObjectDoesNotExist as e:
            user = self.login.user
            social_accounts = user.socialaccount_set.all()
            provider = 'email'
            if social_accounts.exists():
                provider = social_accounts[0].provider
            raise self.DuplicatedEmailError(dict(
                exist=True, platform=provider, login=self.adapter.provider_id,
                email=user.email
            ))

    def check_user(self):
        """
        social login user의 user가 jwt_token user와 다른 경우
        jwt_token user(anonymous user)를 삭제
        21.3.2 -> 삭제 말고 temporary user log를 쌓는 것으로 변경
        신규 유저 -> UserService의 after_signup 함수 실행
        """
        if getattr(self, 'user', None) is None or self.user.is_anonymous:
            self._user = self.login.user

        # if self.user.id != self.login.user.id:
        #     # 기존 소셜 로그인을 한 유저인 경우 -> 온보딩 수준에 따라 덮어쓰기를 진행함.
        #     OnboardingProcessService.check_onboarding_social_user(self.login.user, self.user)
        #     self._user = self.login.user
        #
        # if self.is_new:
        #     service = UserService()
        #     service.after_signup(user=self.user)

    def get_client(self, request, app):
        callback_url = self.get_callback_url()
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client_id = app.client_id
        if ',' in client_id:
            client_ids = client_id.split(",")
            for _client_id in client_ids:
                if self.state is not None:
                    # state가 있다면 web
                    client_id = _client_id if 'web' in _client_id else client_id
                else:
                    # state가 없다면 ios app
                    client_id = _client_id if 'web' not in _client_id else client_id
        client = self.adapter.client_class(
            self.request,
            client_id,
            app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope,
            scope_delimiter=self.adapter.scope_delimiter,
            headers=self.adapter.headers,
            basic_auth=self.adapter.basic_auth,
        )
        return client

    def redirect_url_with_token(self, redirect_url):
        jwt_token = SlidingToken.for_user(self.user)
        if '?' in redirect_url:
            redirect_url += f'&access={str(jwt_token)}&refresh={str(jwt_token)}'
        else:
            redirect_url += f'?access={str(jwt_token)}&refresh={str(jwt_token)}'
        return redirect_url

    def token_serializer(self):
        jwt_token = SlidingToken.for_user(self.user)
        rtn = dict(
            access=str(jwt_token),
            refresh=str(jwt_token)
        )
        return rtn

    def redirect_url_with_error(self, redirect_url, query: Optional[dict] = None):
        if '?' in redirect_url:
            redirect_url += f'&state=fail'
        else:
            redirect_url += f'?state=fail'
        if query is None:
            return redirect_url + f'&login={self.adapter.provider_id}'
        for key, val in query.items():
            if val is True:
                val = 'true'
            elif val is False:
                val = 'false'
            redirect_url += f'&{key}={val}'
        return redirect_url

    def jwt_decode(self, jwt_token) -> dict:
        import jwt
        from WAKe_server.settings import SECRET_KEY
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms='HS256')
            return payload
        except:
            raise self.SocialLoginError(dict(login=self.adapter.provider_id))

    def get_user_by_jwt_token(self, jwt_token):
        payload: dict = self.jwt_decode(jwt_token)
        email = payload.get('user_id')
        user = User.objects.get(email=email)
        self._user = user
        return user

    @property
    def social_account_adapter(self) -> DefaultSocialAccountAdapter:
        """
        DefaultSocialAccountAdapter -> OAuth2Adapter와 다름
        account 처리 하는 용도
        """
        return get_adapter()

    @property
    def adapter(self) -> OAuth2Adapter:
        if self.adapter_class is None:
            raise Exception('you have to set adater_class.')
        if self.request is None:
            raise Exception('you hav to init request parameter.')
        return self.adapter_class(self.request)

    @property
    def social_app(self) -> SocialApp:
        return self.provider.get_app(self.request)

    @property
    def provider(self) -> Provider:
        return self.adapter.get_provider()

    @property
    def token(self):
        token = getattr(self, '_token', None)
        if token is not None:
            return token
        raise self.SocialLoginError(dict(login=self.adapter.provider_id))

    @property
    def user(self):
        if not hasattr(self, '_user'):
            raise self.UserDoesNotExists('You must set _user')
        return self._user

    @property
    def is_new(self):
        return self._is_new