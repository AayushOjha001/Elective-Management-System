"""
WSGI config for PMS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings in production
if os.environ.get('DJANGO_SETTINGS_MODULE'):
    pass  # Use whatever is set
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')

application = get_wsgi_application()