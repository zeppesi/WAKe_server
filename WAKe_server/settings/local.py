from WAKe_server.settings.base import *
from WAKe_server.settings.secrets import get_secrets

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AWS_S3_CUSTOM_DOMAIN = get_secrets('AWS_S3_CUSTOM_DOMAIN')
AWS_STORAGE_BUCKET_NAME = get_secrets('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = get_secrets('AWS_REGION')
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

STATIC_URL = "https://%s/static/" % AWS_S3_CUSTOM_DOMAIN

KAKAO_CLIENT_SECRET = get_secrets('KAKAO_CLIENT_SECRET')
KAKAO_REST_API_KEY = get_secrets('KAKAO_REST_API_KEY')
KAKAO_ADMIN = get_secrets('KAKAO_ADMIN')

DJANGO_SECRET_KEY = get_secrets('DJANGO_SECRET_KEY')
KAKAO_CALLBACK_URI = get_secrets('KAKAO_CALLBACK_URI')
LOGIN_REDIRECT_URL = get_secrets('LOGIN_REDIRECT_URL')
KAKAO_ADMIN_KEY = get_secrets('KAKAO_ADMIN')
BASE_URL = get_secrets('BASE_URL')

SOCIALACCOUNT_PROVIDERS = {
    "kakao": {
        "APP": {
            "client_id": get_secrets('KAKAO_REST_API_KEY'),
            "secret": get_secrets('KAKAO_CLIENT_SECRET')
        }
    },

    "apple": {
        "APP": {
            # Your service identifier.
            # todo apple login시에 알맞게 바꿔야함
            "client_id": "com.bunkerkids.shipdan.web,com.bunkerkids.shipdan",

            # The Key ID (visible in the "View Key Details" page).
            "secret": get_secrets('APPLE_SECRET_KEY'),

            # Member ID/App ID Prefix -- you can find it below your name
            # at the top right corner of the page, or it’s your App ID
            # Prefix in your App ID.
            "key": "V3ZYVUVY76",

            # The certificate you downloaded when generating the key.
            "certificate_key": get_secrets('APPLE_CERTIFICATE_KEY').replace('\\n', '\n')
        }
    }
}