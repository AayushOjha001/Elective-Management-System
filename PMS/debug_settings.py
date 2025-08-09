#!/usr/bin/env python
"""
Debug script to verify Django settings in production
Run this to check which settings module is being used
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("DJANGO SETTINGS DEBUG")
print("=" * 50)

print(f"Environment Variables:")
print(f"  DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"  DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
print(f"  ALLOWED_HOSTS: {os.environ.get('ALLOWED_HOSTS', 'NOT SET')}")
print(f"  SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")

# Force the production settings
if os.environ.get('DEBUG', '1') == '0':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')

print(f"\nAfter setdefault:")
print(f"  DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    import django
    django.setup()
    
    from django.conf import settings
    
    print(f"\nDjango Configuration:")
    print(f"  Settings module: {settings.SETTINGS_MODULE}")
    print(f"  DEBUG: {settings.DEBUG}")
    print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"  SECRET_KEY: {'SET' if settings.SECRET_KEY else 'NOT SET'}")
    print(f"  Database ENGINE: {settings.DATABASES['default']['ENGINE']}")
    print(f"  Database NAME: {settings.DATABASES['default']['NAME']}")
    
    # Test if the current hostname would be allowed
    test_hosts = [
        'elective-management-system.onrender.com',
        'localhost',
        '127.0.0.1',
        '0.0.0.0'
    ]
    
    print(f"\nHost validation test:")
    for host in test_hosts:
        allowed = host in settings.ALLOWED_HOSTS or '*' in settings.ALLOWED_HOSTS
        print(f"  {host}: {'✅ ALLOWED' if allowed else '❌ BLOCKED'}")
        
except Exception as e:
    print(f"\n❌ Error loading Django settings: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
