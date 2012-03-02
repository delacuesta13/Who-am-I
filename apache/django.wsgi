import os
import sys

sys.path.append('/var/django/projects')
sys.path.append('/var/django/projects/whoami')

os.environ['DJANGO_SETTINGS_MODULE'] = 'whoami.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()