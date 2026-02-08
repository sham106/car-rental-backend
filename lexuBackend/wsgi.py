"""
WSGI config for lexuBackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

# Patch tempfile for Windows compatibility before Django loads
from lexuBackend.tempfile_patch import _patch_tempfile
_patch_tempfile()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexuBackend.settings')

application = get_wsgi_application()
