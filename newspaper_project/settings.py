
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRECT_KEY','clave-por-defecto-solo-para-desarrollo-local')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
#DEBUG = 'True'

# ==========================================
# 2. ALLOWED_HOSTS A PRUEBA DE FALLOS PARA RENDER
# ==========================================
# Render inyecta automáticamente esta variable en sus servidores.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    # Entorno de Producción (Render)
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '.onrender.com', '127.0.0.1', 'localhost']
else:
    # Entorno de Desarrollo Local
    ALLOWED_HOSTS = ['django-periodico.onrender.com', '127.0.0.1', 'localhost']

"""ALLOWED_HOSTS = [
    #os.environ.get('DJANGO_HOSTS', '127.0.0.1,localhost').split(',')
    'django-periodico.onrender.com',
    '.onrender.com',
    '127.0.0.1',
    'localhost',
]"""
#ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://django-periodico.onrender.com',
    'https://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party
    'rest_framework',
    'rest_framework.authtoken',
    'cloudinary_storage',
    'cloudinary',
    # Local
    'news',
    'users',
    'tinymce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'newspaper_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'news.context_processors.site_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'newspaper_project.wsgi.application'



#  Configuración de base de datos adaptable
if os.environ.get('DATABASE_URL'):
    # Producción: usar DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True  # Cambiar a False para desarrollo
        )
    }
else:
    # Desarrollo local: configuración directa
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'newspaper_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'theme': 'silver',
    'menubar': True,
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
        'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'media', 'table', 'help', 'wordcount'
    ],
    'toolbar': [
        'undo redo | blocks | bold italic underline strikethrough |',
        'alignleft aligncenter alignright alignjustify |',
        'bullist numlist outdent indent | link image media table |',
        'removeformat code | help'
    ],
    'content_css': '/static/css/tinymce.css',
    'image_advtab': True,
    'file_picker_types': 'image',
    'automatic_uploads': True,
    'images_upload_url': '/tinymce/upload/',
    'relative_urls': False,
    'remove_script_host': False,
    
    # Permitir iframes para videos embebidos
    'extended_valid_elements': 'iframe[src|width|height|name|align|class|frameborder|allowfullscreen|allow|style]',
    'valid_elements': '*[*]',
}


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- NUEVA CONFIGURACIÓN DE ALMACENAMIENTO PARA DJANGO 5.x ---
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

AUTH_USER_MODEL = 'users.CustomUser'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 10,
}

MEDIA_URL ='/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#--- CONFIGURACION DE CLOUDINARY ---
CLOUDINARY_STORAGE = {
    #'CLOUD_NAME': os.environ.get('vtey0sct'),
    #'API_KEY': os.environ.get('966914473537684'),
    #'API_SECRET': os.environ.get('YtLGk70j8VnBVY96ABjWE3V34qA'),

    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Usar Cloudinary para archivos media
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'