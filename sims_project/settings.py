"""
Django settings for sims_project.

SIMS - Postgraduate Medical Training System
A comprehensive platform for managing postgraduate medical training,
rotations, certificates, workshops, logbooks, and clinical cases.

Created: 2025-05-29 16:07:57 UTC
Author: SMIB2012

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,testserver,172.236.152.35').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For number formatting
      # Third-party apps
    'crispy_forms',              # For better form rendering
    'crispy_bootstrap5',         # Bootstrap 5 support for forms
    'import_export',             # For CSV/Excel import/export
    'rest_framework',            # For API endpoints
    'django_filters',            # For advanced filtering
    'widget_tweaks',             # For form widget customization
      # SIMS apps
    'sims.users',
    'sims.rotations',
    'sims.certificates',
    'sims.logbook',
    'sims.cases',
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

ROOT_URLCONF = 'sims_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Global templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sims.context_processors.admin_stats_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sims_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        
        # For production, use PostgreSQL:
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'sims_db',
        # 'USER': 'sims_user',
        # 'PASSWORD': 'your_password',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Only include static directory if it exists and has content
STATICFILES_DIRS = []
static_dir = BASE_DIR / 'static'
if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

# Session settings
SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Security settings (adjust for production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# For production, enable these:
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Django Messages Framework
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# For production:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'your-smtp-server.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@domain.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'

DEFAULT_FROM_EMAIL = 'SIMS System <noreply@sims.medical.edu>'
ADMIN_EMAIL = 'admin@sims.medical.edu'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Allowed file extensions for uploads
ALLOWED_UPLOAD_EXTENSIONS = [
    '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xlsx', '.xls', '.csv'
]

# Maximum file size for uploads (in bytes)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# SIMS Specific Settings
SIMS_SETTINGS = {
    # System Information
    'SYSTEM_NAME': 'SIMS - Postgraduate Medical Training System',
    'SYSTEM_VERSION': '1.0.0',
    'INSTITUTION_NAME': 'Medical College',
    'INSTITUTION_ADDRESS': 'Medical College Address',
    'CONTACT_EMAIL': 'contact@sims.medical.edu',
    'CONTACT_PHONE': '+1-234-567-8900',
    
    # Training Settings
    'DEFAULT_ROTATION_DURATION_MONTHS': 6,
    'MIN_LOGBOOK_ENTRIES_PER_ROTATION': 10,
    'MIN_CASES_PER_YEAR': 50,
    'REQUIRED_WORKSHOP_HOURS_PER_YEAR': 40,
    
    # Document Review Settings
    'AUTO_APPROVE_CERTIFICATES': False,
    'REVIEW_DEADLINE_DAYS': 7,
    'REMINDER_DAYS_BEFORE_DEADLINE': 2,
    
    # Notification Settings
    'SEND_EMAIL_NOTIFICATIONS': True,
    'SEND_SMS_NOTIFICATIONS': False,
    'NOTIFICATION_BATCH_SIZE': 50,
    
    # Analytics Settings
    'ENABLE_ANALYTICS': True,
    'ANALYTICS_RETENTION_MONTHS': 24,
    'GENERATE_MONTHLY_REPORTS': True,
    
    # Security Settings
    'ENABLE_TWO_FACTOR_AUTH': False,
    'PASSWORD_EXPIRY_DAYS': 90,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION_MINUTES': 30,
    
    # Backup Settings
    'AUTO_BACKUP_ENABLED': True,
    'BACKUP_RETENTION_DAYS': 30,
    'BACKUP_LOCATION': BASE_DIR / 'backups',
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'sims.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'sims': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Cache Configuration (for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# For production with Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Celery Configuration (for background tasks)
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE

# Import/Export Settings
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.TempFolderStorage'

# Django Extensions (if using)
# INSTALLED_APPS += ['django_extensions']

# Environment-specific settings
if DEBUG:
    # Development settings
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    # Debug toolbar (if installed)
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
    except ImportError:
        pass

else:
    # Production settings
    SECURE_SSL_REDIRECT = False  # Set to True when SSL is configured
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = False  # Set to True when SSL is configured
    CSRF_COOKIE_SECURE = False  # Set to True when SSL is configured
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,172.236.152.35').split(',')
    
    # Database from environment (SQLite for now, PostgreSQL for full production)
    if os.environ.get('DB_NAME'):
        DATABASES['default'].update({
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        })
    
    # Email settings from environment
    if os.environ.get('EMAIL_HOST'):
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = os.environ.get('EMAIL_HOST')
        EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
        EMAIL_USE_TLS = True
        EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Load local settings if available
try:
    from .local_settings import *
except ImportError:
    pass