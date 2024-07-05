from WAKe_server.settings.base import *
from WAKe_server.settings import get_secrets

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secrets('DATABASE_NAME'),
        'USER': get_secrets('DATABASE_USER'),
        'PASSWORD': get_secrets('DATABASE_PASSWORD'),
        'HOST': get_secrets('DATABASE_HOST'),
        'PORT': get_secrets('DATABASE_PORT'),
    }
}

AWS_S3_CUSTOM_DOMAIN = get_secrets('AWS_S3_CUSTOM_DOMAIN')
AWS_STORAGE_BUCKET_NAME = get_secrets('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = get_secrets('AWS_REGION')
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

STATIC_URL = "https://%s/static/" % AWS_S3_CUSTOM_DOMAIN