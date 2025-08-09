#!/bin/bash

# Force Django settings module
export DJANGO_SETTINGS_MODULE=PMS.settings_production

# Run Django management commands with forced settings
python manage.py "$@" --settings=PMS.settings_production
