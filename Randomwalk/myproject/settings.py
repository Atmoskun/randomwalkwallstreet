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
# NOTE: .env file is expected to be located in the same directory as manage.py
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(DOTENV_PATH)

# CRITICAL DEBUG: Check if the key was loaded from the .env file (for local testing)
google_key_check = os.environ.get('GOOGLE_API_KEY')
if google_key_check:
    print(f"SETTINGS DEBUG: Successfully loaded GOOGLE_API_KEY (First 4 chars: {google_key_check[:4]})")
else:
    print(f"SETTINGS DEBUG: WARNING! GOOGLE_API_KEY not found in environment after loading {DOTENV_PATH}")


# ---
# SECURITY & DEBUG
# ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key-for-local')

# Reads DEBUG setting from environment, defaults to False for safety
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ---
# 1. ALLOWED HOSTS (Corrected and Consolidated Block)
# ---
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '::1']

# Standard Render external hostname configuration
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Explicitly add the specific Render and Codespaces domains and internal host for deployment stability
ALLOWED_HOSTS.extend([
    'randomwalkwallstreet.onrender.com', 
    'webserver', # Internal hostname for Render container
    # Add your codespaces domain pattern here if needed, or rely on the host being proxied correctly
])

# ---
# 2. CSRF Trusted Origins (For deployment environments)
# ---
# This is required to prevent CSRF errors when submitting forms from certain origins (like proxies/ports).
CSRF_TRUSTED_ORIGINS = [
    'https://localhost:8000', 
    'http://localhost:8000', 
    'https://127.0.0.1:8000',
    'http://127.0.0.1:8000',
    'https://randomwalkwallstreet.onrender.com',
]

# FIX: Only append the dynamic Render host if the environment variable is set.
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


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
    'tracking',       
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must come right after SecurityMiddleware for static file handling
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tracking.middleware.PageViewMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# ---
# TEMPLATES 
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


# Password validation (Standard)
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization (Standard)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True


# ---
# STATIC FILES (WhiteNoise/Render Configuration)
# ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use the CompressedManifestStaticFilesStorage backend for WhiteNoise in production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
