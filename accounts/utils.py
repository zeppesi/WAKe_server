from rest_framework_simplejwt.tokens import SlidingToken


def token_serializer(user):
    jwt_token = SlidingToken.for_user(user)
    rtn = dict(
        access=str(jwt_token),
        refresh=str(jwt_token)
    )
    return rtn
