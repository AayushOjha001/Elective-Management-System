import os
import dj_database_url
from .settings import *

# Production settings
DEBUG = False

# Secret key from environment or fallback for build
SECRET_KEY = os.environ.get('SECRET_KEY', '7u$p-*j3mykg2@)8p#hwa639=tlgol-f0o-9omkb(75*zdxu4&')

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allowed hosts - VERY EXPLICIT
ALLOWED_HOSTS = [
    'elective-management-system.onrender.com',
    '*.onrender.com',
    'electivemanagent.itclub.asmitphuyal.com.np',
    'itclub.asmitphuyal.com.np',
    '*.itclub.asmitphuyal.com.np',
    'localhost',
    '127.0.0.1',
    '0.0.0.0'
]

# Add from environment variable too
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS.extend(ALLOWED_HOSTS_ENV.split(','))

# Remove duplicates and empty strings
ALLOWED_HOSTS = list(set([h.strip() for h in ALLOWED_HOSTS if h.strip()]))

print(f"🔧 Production ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔧 Total hosts configured: {len(ALLOWED_HOSTS)}")
for i, host in enumerate(ALLOWED_HOSTS):
    print(f"   {i+1}. '{host}'")

# Database configuration for production
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Use SQLite with persistent disk volume
    DATABASE_DIR = '/app/data' if os.path.exists('/app/data') else os.path.join(BASE_DIR, 'data')
    try:
        os.makedirs(DATABASE_DIR, exist_ok=True)
        # Test write permissions
        test_file = os.path.join(DATABASE_DIR, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"✅ Database directory ready: {DATABASE_DIR}")
    except Exception as e:
        print(f"❌ Database directory error: {e}")
        # Fallback to local directory
        DATABASE_DIR = os.path.join(BASE_DIR, 'data')
        os.makedirs(DATABASE_DIR, exist_ok=True)
        print(f"Using fallback database directory: {DATABASE_DIR}")
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(DATABASE_DIR, 'db.sqlite3'),
        }
    }

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
