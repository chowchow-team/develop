from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = read_secret('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['챠우챠우(미정).com'] # 도메인 구입 후 변경

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "chow",
        "USER": "chow",
        "PASSWORD": read_secret('MYSQL_PASSWORD'),
        "HOST": "mariadb",
        "PORT": "3306",
    }
}

# Redis Channel Layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("redis", 6379)],  # Redis 서버 주소
        },
    },
}

CSRF_TRUSTED_ORIGINS = [
    'https://챠우챠우(미정).com',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FROM_EMAIL = 'chow3mail@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'chow3mail@gmail.com'  # 이메일 계정
EMAIL_HOST_PASSWORD = read_secret('EMAIL_HOST_PASSWORD')   # 이메일 비밀번호
EMAIL_USE_TLS = True

CRONJOBS=[
    ('0 6 * * *', 'accountapp.cron.my_scheduled_job'),
    ('*/1 * * * *', 'llmapp.cron.update_animals'),
]

from django.conf import settings
CRONTAB_COMMAND_PREFIX = f'cd {settings.BASE_DIR} && '