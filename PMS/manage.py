#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    # Use production settings in production environment, fall back to development settings
    if os.environ.get('DEBUG', '1') == '0':
        # Production environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings_production')
    else:
        # Development environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
