"""
Django settings for myproject project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR should point to the 'Randomwalk' directory in your structure.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---
# Load .env file from the project root (one level above this 'myproject' folder)
# This handles our GOOGLE_API_KEY, DEBUG, and SECRET_KEY for local testing.
# ---
load_dotenv(os.path.join(BASE_DIR, ".env"))


# ---
# SECURITY & DEBUG
# ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-local')

# Reads DEBUG setting from environment, defaults to False for safety
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED HOSTS
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '::1']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For development static files
    'django.contrib.staticfiles',
    # Your project apps
    'mailinglist', 
    'api',         
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # For production static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# ---
# TEMPLATES (The critical section for your last error)
# ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS lists the base template folders to check first
        'DIRS': [
            # We explicitly tell Django to look in Randomwalk/api/templates/
            BASE_DIR / 'api/templates', 
            BASE_DIR / 'mailinglist/templates',
        ],
        'APP_DIRS': True, # Also look in app/templates folders
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

WSGI_APPLICATION = 'myproject.wsgi.application'


# ---
# DATABASE
# ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Use PostgreSQL for Render deployment if URL is present
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL'))


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---
# STATIC FILES (For Whitenoise/Render)
# ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py

# ALLOWED_HOSTS
# A list of strings representing the host/domain names that this Django site can serve.
# When DEBUG is False, this is a security measure to prevent HTTP Host header attacks.
# We include 'localhost' and '127.0.0.1' for local development.
# If you are accessing the server using its network IP (e.g., 192.168.x.x), you should add that here too.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '::1']


# settings.py

# CSRF_TRUSTED_ORIGINS
# A list of trusted origins for unsafe requests (like POST) when the Origin header is present.
# The error message shows the failed origin is 'https://localhost:8000'.
# We add both HTTP and HTTPS versions for localhost development on port 8000 to cover all cases.
CSRF_TRUSTED_ORIGINS = [
    'https://localhost:8000', 
    'http://localhost:8000', 
    'https://127.0.0.1:8000',
    'http://127.0.0.1:8000',
]
