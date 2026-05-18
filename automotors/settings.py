"""
Django settings — AutoMotors (TPIII_SASI)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECRET_KEY = 'django-insecure-^95g&ts$0xg-veiwu15mkr)f#f@3btw5$vbpu4k!1n##+r)l&b'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'www.automotors.com', 'automotors.local']

# ============================================================================
#  HTTPS SELETIVO — AutoMotors
# ============================================================================
# Estratégia: dois servidores Django em paralelo.
#   HTTP  → runserver         na porta 8000  (páginas públicas)
#   HTTPS → runsslserver      na porta 8443  (páginas com dado sensível)
#
# O decorator @ssl_required redireciona automaticamente para HTTPS quando
# o usuário acessa uma rota sensível via HTTP. O decorator @http_only faz
# o caminho inverso, devolvendo a navegação pública pra HTTP por economia
# de processamento (e para cumprir a exigência do enunciado de NÃO ter
# HTTPS global — sob pena de perder 60% da nota).
AUTOMOTORS_HTTP_HOST  = 'localhost:8000'
AUTOMOTORS_HTTPS_HOST = 'localhost:8443'

# CSRF deve aceitar requisições vindas dos dois protocolos.
CSRF_TRUSTED_ORIGINS = [
    f'http://{AUTOMOTORS_HTTP_HOST}',
    f'https://{AUTOMOTORS_HTTPS_HOST}',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8443',
]

# Cookies de sessão precisam fluir entre HTTP e HTTPS — não podem ser Secure-only.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Nunca forçar HTTPS global (cai no -60% da nota).
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Para que reverse-proxy informe o protocolo real ao Django.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sslserver',  # python manage.py runsslserver
    'home',
    'garagem',
    'acessorios',
    'cart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'automotors.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.protocolo_hosts',
            ],
        },
    },
]

WSGI_APPLICATION = 'automotors.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
