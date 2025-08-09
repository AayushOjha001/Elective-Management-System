"""
WSGI config for PMS project - PRODUCTION VERSION
This file explicitly uses production settings.
"""

import os
from django.core.wsgi import get_wsgi_application

# FORCE production settings - no environment variable checks
os.environ['DJANGO_SETTINGS_MODULE'] = 'PMS.settings_production_clean'

application = get_wsgi_application()
