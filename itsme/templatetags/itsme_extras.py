# -*- coding: iso-8859-1 -*-

from django import template
from itsme.bbcodeparser import BBCodeParser 

register = template.Library()

@register.filter
def remove_bbcode(s):
    content_bbcode = BBCodeParser(s)
    return content_bbcode.remove_bbcode(s)