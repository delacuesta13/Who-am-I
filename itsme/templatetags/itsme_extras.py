# -*- coding: iso-8859-1 -*-

from django import template
from itsme.bbcodeparser import BBCodeParser 

register = template.Library()

@register.filter
def remove_bbcode(s):
    content_bbcode = BBCodeParser(s)
    return content_bbcode.remove_bbcode(s)

@register.filter
def post_get_description(s):
    """Return description of a content."""
    content_bbcode = BBCodeParser(s)
    if len(content_bbcode.get_all_paragraphs()) > 0:
        content_bbcode = content_bbcode.bbcode_to_html(content_bbcode.get_all_paragraphs()[0])
        content_bbcode = '<p>' + content_bbcode + '</p>'
    elif len(content_bbcode.get_all_pictures()) > 0:
        content_bbcode = content_bbcode.get_all_pictures()[0]
        content_bbcode = '<p>' + '<img src="' + content_bbcode[1] + '" alt="' + content_bbcode[0] + '">' + '</p>'
    elif len(content_bbcode.get_all_youtube()) > 0:
        video_id = content_bbcode.get_all_youtube()[0]
        content_bbcode = '<div class="video-wrapper"><div class="video-container">'
        content_bbcode += '<iframe src="http://www.youtube.com/embed/' + video_id
        content_bbcode += '" width="600" height="361" frameborder="0" allowFullScreen></iframe>'
        content_bbcode += '</div></div>'
    elif len(content_bbcode.get_all_vimeo()) > 0:
        video_id = content_bbcode.get_all_vimeo()[0]
        content_bbcode = '<div class="video-wrapper"><div class="video-container">'
        content_bbcode += '<iframe src="http://player.vimeo.com/video/' + video_id
        content_bbcode += '?byline=0&amp;portrait=0" width="600" height="361" frameborder="0" allowFullScreen></iframe>'
        content_bbcode += '</div></div>'
    else:
        content_bbcode = '<p><em>There isn\'t description for this blog post.</em></p>'
    return content_bbcode

@register.filter
def content_get_media(s):
    bbcode_to_html = BBCodeParser(s)
    content = bbcode_to_html.get_html_from_bbcode_tags(bbcode_to_html.escape_html(), 
                                                       True,
                                                       *bbcode_to_html.get_media_tags())
    return content

@register.filter
def content_get_info(s):
    """Remove all media tags"""
    bbcode_to_html = BBCodeParser(s)
    info_tags = [tag for tag in bbcode_to_html.bbcode_rules.iterkeys() if tag not in bbcode_to_html.get_media_tags()]
    content = bbcode_to_html.get_html_from_bbcode_tags(bbcode_to_html.escape_html(), 
                                                       True, 
                                                       *info_tags)
    return content    
