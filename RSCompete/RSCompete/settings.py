"""
Django settings for RSCompete project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*khpkn_ti(kmcm_=ujkrzh$qqjxau14k64hvp@v@4f5qwa8)bx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

#add the support of send email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_USE_TLS = False   #是否使用TLS安全传输协议(用于在两个通信应用程序之间提供保密性和数据完整性。)
#EMAIL_USE_SSL = True    #是否使用SSL加密，qq企业邮箱要求使用
#EMAIL_HOST = 'smtp.163.com'   #发送邮件的邮箱 的 SMTP服务器，这里用了163邮箱
#EMAIL_PORT = 465     #发件箱的SMTP服务器端口
#EMAIL_HOST_USER = 'rssrai2019@163.com'    #发送邮件的邮箱地址
#EMAIL_HOST_PASSWORD = 'Duccsu123'         #发送邮件的邮箱密码(这里使用的是授权码
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'rscup2019@hotmail.com'
EMAIL_HOST_PASSWORD = 'whu2019csu'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'RSCompeteAPI',
    'django_celery_results',
    'django_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'RSCompete.urls'
CORS_ALLOW_CREDENTIALS=True
CORS_ORIGIN_ALLOW_ALL = True
#CORS_ORIGIN_WHITELIST = ["http://localhost:4444"]
CORS_ALLOW_METHODS = ('POST', 'GET', 'DELETE','OPTIONS','PATCH','PUT','VIEW')
CORS_ALLOW_HEADERS = ('XMLHttpRequest','X_FILENAME','accept-encoding','authorization','content-type','dnt','origin','user-agent','x-csrftoken','x-requested-with')


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RSCompete.wsgi.application'
SESSION_COOKIE_SAMESITE=None

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE':'django.db.backends.mysql',
        'NAME':'RSCompete',
        'USER':"RSAdmin",
        'PASSWORD':"xuan",
        'HOST':"",
        'PORT':"",
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

APPEND_SLASH=False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/data'
#STATICFILES_DIRS = ("/home/xuan/ducRemoteSenseCompete/static") 

CRONJOBS = [('1 8 * * *', 'RSCompeteAPI.cron.generate_leaderboard',">> /home/xuan/crontab.log"), ('1 8 * * *', 'RSCompeteAPI.cron.get_result',">> /home/xuan/crontab.log")]
# CRONJOBS = [('1 8 * * *', 'RSCompeteAPI.cron.generate_leaderboard',">> /home/xuan/crontab.log")]
CELERY_RESULT_BACKEND = 'django-db'

CELERY_BROKER_URL = 'amqp://RS:147258123@192.168.1.189:5672/RS_host'
