import os
from pathlib import Path
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY','dev-only-change-me')
DEBUG = os.getenv('DJANGO_DEBUG','1') == '1'
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','corsheaders','rest_framework','drf_spectacular','core']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware','django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.mysql','NAME':os.getenv('MYSQL_DATABASE','credit_card_db'),'USER':os.getenv('MYSQL_USER','credituser'),'PASSWORD':os.getenv('MYSQL_PASSWORD','creditpass'),'HOST':os.getenv('MYSQL_HOST','mysql'),'PORT':os.getenv('MYSQL_PORT','3306')}}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'}]
LANGUAGE_CODE='en-us'; TIME_ZONE='Asia/Kolkata'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS=True
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':('rest_framework_simplejwt.authentication.JWTAuthentication',),'DEFAULT_PERMISSION_CLASSES':('rest_framework.permissions.IsAuthenticated',),'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema'}
SIMPLE_JWT={'ACCESS_TOKEN_LIFETIME':timedelta(minutes=30),'REFRESH_TOKEN_LIFETIME':timedelta(days=1)}
SPECTACULAR_SETTINGS={'TITLE':'Credit Card Payment System API','VERSION':'1.0.0'}
