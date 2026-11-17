"""
WSGI config for superr_selector project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'superr_selector.settings')

application = get_wsgi_application()

# Vercel Python runtime expects the callable to be named 'app'
app = application
