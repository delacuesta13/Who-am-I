# -*- coding: iso-8859-1 -*-

from django.conf import settings

def base_site_url(context):
    """Return values for use them on templates."""
    return {'BASE_URL': settings.BASE_URL}