"""
Конфигурация приложения с PostgreSQL
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent

# Настройки базы данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'desktop_app_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Настройки Django
INSTALLED_APPS = [
    'database',
]

SECRET_KEY = os.getenv('SECRET_KEY', 'desktop-app-secret-key-12345-change-this')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Язык и время
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Отключаем ненужные для desktop приложения настройки
MIDDLEWARE = []
ROOT_URLCONF = ''
WSGI_APPLICATION = ''
ASGI_APPLICATION = ''
TEMPLATES = []
AUTH_PASSWORD_VALIDATORS = []