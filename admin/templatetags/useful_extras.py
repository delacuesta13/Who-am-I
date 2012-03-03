# -*- coding: iso-8859-1 -*-

from django import template

register = template.Library()

@register.filter
def get_val_from_dictionary(dict_, key):
    """Return value from a dictionary key."""
    return dict_[key]
