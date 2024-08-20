from dataclasses import dataclass, field
from typing import Optional, List

from dtos.base import BaseOutputDTO, BaseInputDTO


@dataclass
class OauthStateInputDTO(BaseInputDTO):
    redirect: str
    jwt_token: Optional[str] = None

    dto_name: str = field(default='ouath_state', init=False)


@dataclass
class KakaoOauthTokenOutputDTO(BaseOutputDTO):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int
    scope: List[str]

    dto_name: str = field(default='kakao_oauth_token', init=False)


@dataclass
class KakaoChannelRelationOutputDTO(BaseOutputDTO):
    state: bool

    dto_name: str = field(default='kakao_channel_relation', init=False)
