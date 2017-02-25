"""
WSGI config for osbb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, root)
packages = '/var/www/.virtualenvs/hoa/lib/python3.4/site-packages'
sys.path.insert(0, packages)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osbb.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
