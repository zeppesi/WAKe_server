from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import SlidingToken


class CustomAuthenticationMiddleware(MiddlewareMixin):

    def set_jwt_cookie(self, request: WSGIRequest, response: Response):
        if request.user.is_authenticated:
            jwt = SlidingToken.for_user(request.user)
            origin = request.headers.get('origin')
            is_local = False if origin is None or 'localhost' not in origin else True
            domain = None if is_local else '.zps.kr'
            response.set_cookie(
                'jwt',
                str(jwt),
                max_age=3600 * 24 * 3,
                domain=domain,
                secure=(not is_local),
                httponly=True,
                samesite=False,
            )
        elif request.COOKIES.get('jwt', None) is not None:
            response.set_cookie(
                'jwt', max_age=0, domain='.zps.kr', secure=True,
                expires='Thu, 01 Jan 1970 00:00:00 GMT', samesite=False,
            )

        return response

    def process_response(self, request, response):
        return self.set_jwt_cookie(request, response)
