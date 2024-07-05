from WAKe_server.settings.base import *
from WAKe_server.settings.secrets import get_secrets

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "wake",
    }
}

AWS_S3_CUSTOM_DOMAIN = get_secrets('AWS_S3_CUSTOM_DOMAIN')
AWS_STORAGE_BUCKET_NAME = get_secrets('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = get_secrets('AWS_REGION')
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

STATIC_URL = "https://%s/static/" % AWS_S3_CUSTOM_DOMAIN