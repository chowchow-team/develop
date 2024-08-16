from .base import *

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Redis Channel Layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Redis 서버 주소
        },
    },
}

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FROM_EMAIL = 'chow3mail@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'chow3mail@gmail.com'  # 이메일 계정
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')   # 이메일 비밀번호
EMAIL_USE_TLS = True

ANIMAL_API_KEY = env('ANIMAL_API_KEY')

CRONJOBS=[
    ('*/1 * * * *', 'accountapp.cron.my_scheduled_job'),
    ('*/1 * * * *', 'llmapp.cron.update_animals'),
]

from django.conf import settings
CRONTAB_COMMAND_PREFIX = f'cd {settings.BASE_DIR} && '