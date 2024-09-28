from accounts.models import User
from rest_framework_simplejwt.tokens import SlidingToken


def get_sliding_token(email: str):
    user = User.objects.get(email=email)
    return str(SlidingToken.for_user(user))
