"""
WSGI config for PMS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings in production environment, fall back to development settings
if os.environ.get('DEBUG', '1') == '0':
    # Production environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings_production')
else:
    # Development environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')

application = get_wsgi_application()
