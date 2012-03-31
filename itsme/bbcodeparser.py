# -*- coding: iso-8859-1 -*-

import re
from django.template.defaultfilters import force_escape

class BBCodeParser:

    bbcode_rules = {
        'heading': {
                    'sub': [
                            r'\[h([1-6]{1})\](.*?)\[/h([1-6]{1})\]', # Regex to find BBCode tag
                            r'<h\1>\2</h\1>', # Replace from BBCode to HTML
                            r'\2', # Remove BBCode
                            ],
                    },
        'paragraph': {
                      'sub': [
                              r'\[p\](.*?)\[/p\]', 
                              r'<p>\1</p>', 
                              r'\1',
                              ],
                      'findall': r'\[p\](.*?)\[/p\]', # find in content this BBCode tag
                      },
        'color': {
                  'sub': [
                          r'\[color=(#[0-9a-fA-F]{3,6}|[a-zA-Z]+?)\](.*?)\[/color\]',
                          r'<span style="color: \1;">\2</span>', 
                          r'',
                          ],
                  },
        'size': {
                 'sub': [
                         r'\[size=(\d+?)\](.*?)\[/size\]',
                         r'<span style="font-size: \1px;">\2</span>',
                         r'',
                         ],
                 },
        'bold': {
                 'sub': [
                         r'\[b\](.*?)\[/b\]', 
                         r'<strong>\1</strong>',
                         r'\1',
                         ],
                 },
        'italic': {
                   'sub': [
                           r'\[i\](.*?)\[/i\]', 
                           r'<em>\1</em>',
                           r'\1',
                           ],
                   },
        'Stroke through': {
                           'sub': [
                                   r'\[del\](.*?)\[/del\]', 
                                   r'<del>\1</del>',
                                   r'\1',
                                   ],
                           },
        'center': {
                   'sub': [
                           r'\[center\](.*?)\[/center\]',
                           r'<div style="text-align: center;">\1</div>',
                           r'\1',
                           ],
                   },
        'bulleted list': {
                          'sub': [
                                  r'\[list\](.*?)\[/list\]',
                                  r'<ul>\1</ul>',
                                  r'',
                                  ],
                          },
        'numeric list': {
                         'sub': [
                                 r'\[list=(\d+?)\](.*?)\[/list\]',
                                 r'<ol start="\1">\2</ol>',
                                 r'',
                                 ],
                         },
        'list item': {
                      'sub': [
                              r'\[\*\]\s*(.*?)$',
                              r'\t<li>\1</li>',
                              r'\1',
                              ],
                      },
        'quote': {
                  'sub': [
                          r'\[quote=(.+?)\](.*?)\[/quote\]',
                          r'<blockquote><p>\2</p><small>\1</small></blockquote>',
                          r'\2',
                          ],
                  },
        'quote without author': {
                  'sub': [
                          r'\[quote](.*?)\[/quote\]',
                          r'<blockquote><p>\1</p></blockquote>',
                          r'\2',
                          ],
                  },
        'code': {
                 'sub': [
                         r'\[code\](.*?)\[/code\]',
                         r'<pre class="prettyprint linenums">\1</pre>',
                         r'\1'
                         ],
                 },
        'link': {
                 'sub': [
                         r'\[url=(.*?)\](.*?)\[/url\]', 
                         r'<a href="\1">\2</a>',
                         r'\2',
                         ],
                 },
        'picture': {
                    'sub': [
                            r'\[img\s+alt=(?:&quot;|")?(.*?)(?:&quot;|")?\](.*?)\[/img\]',
                            r'<p><img src="\2" alt="\1"></p>',
                            r''
                            ],
                    'findall': r'\[img\s+alt=(?:&quot;|")?(.*?)(?:&quot;|")?\](.*?)\[/img\]',
                    'media': True,
                    },
        'youtube': {
                    'sub': [
                            r'\[youtube\s+width=(\d*?)\s+height=(\d*?)\](.*?)\[/youtube\]',
                            r'<div class="video-wrapper">\n\t<div class="video-container">\n\t\t<iframe src="http://www.youtube.com/embed/\3" width="\1" height="\2" frameborder="0" allowFullScreen></iframe>\n\t</div>\n</div>',
                            r'',
                            ],
                    'findall': r'\[youtube\s+width=\d*?\s+height=\d*?\](.*?)\[/youtube\]',
                    'media': True,
                    },
        'vimeo': {
                  'sub': [
                          r'\[vimeo\s+width=(\d*?)\s+height=(\d*?)\](.*?)\[/vimeo\]',
                          r'<div class="video-wrapper">\n\t<div class="video-container">\n\t\t<iframe src="http://player.vimeo.com/video/\3?byline=0&amp;portrait=0" width="\1" height="\2" frameborder="0" allowFullScreen></iframe>\n\t</div>\n</div>',
                          r'',
                          ],
                  'findall': r'\[vimeo\s+width=\d*?\s+height=\d*?\](.*?)\[/vimeo\]',
                  'media': True,
                  },        
    }
    
    def __init__(self, bbcode):
        self.bbcode = bbcode
    
    def escape_html(self, s=''):
        """Return an escaped string of HTML."""
        escaped_str = s if len(s) > 0 else self.bbcode
        return force_escape(escaped_str)
    
    def bbcode_to_html(self, s=''):
        s = s if len(s) > 0 else self.bbcode
        for value in self.bbcode_rules.itervalues():
            re_bbcode = re.compile(value['sub'][0], re.MULTILINE|re.DOTALL|re.IGNORECASE)
            s = re_bbcode.sub(value['sub'][1], s)
        return s

    def get_all_paragraphs(self):
        return re.findall(self.bbcode_rules['paragraph']['findall'], self.bbcode)
    
    def get_all_pictures(self):
        return re.findall(self.bbcode_rules['picture']['findall'], self.bbcode)
    
    def get_all_youtube(self):
        return re.findall(self.bbcode_rules['youtube']['findall'], self.bbcode)
    
    def get_all_vimeo(self):
        return re.findall(self.bbcode_rules['vimeo']['findall'], self.bbcode)
    
    def remove_bbcode(self, s='', *tags):
        without_bbcode = s if len(s) > 0 else self.bbcode
        if len(tags) != 0:
            for tag in tags:
                if tag in self.bbcode_rules:
                    re_bbcode = re.compile(self.bbcode_rules[tag]['sub'][0], re.MULTILINE|re.DOTALL|re.IGNORECASE)
                    without_bbcode = re_bbcode.sub(self.bbcode_rules[tag]['sub'][2], without_bbcode)
        else:
            for value in self.bbcode_rules.itervalues():
                re_bbcode = re.compile(value['sub'][0], re.MULTILINE|re.DOTALL|re.IGNORECASE)
                without_bbcode = re_bbcode.sub(value['sub'][2], without_bbcode)
        return without_bbcode
    
    def get_html_from_bbcode_tags(self, s='', remove_other_tags=False, *tags):
        """Return content of received tags.
        
        remove_other_tags, boolean
        true, return html content of received bbcode tags and remove content of bbcode tags not specified
        false, return html content of received bbcode tags, but not remove content of bbcode tags no specified
        """
        content = s if len(s) > 0 else self.bbcode
        for tag in tags:
            if tag in self.bbcode_rules:
                re_bbcode = re.compile(self.bbcode_rules[tag]['sub'][0], 
                                       re.MULTILINE|re.DOTALL|re.IGNORECASE)
                content = re_bbcode.sub(self.bbcode_rules[tag]['sub'][1], 
                                        content)
        if remove_other_tags:
            tags_not_specified = [tag for tag in self.bbcode_rules.iterkeys() if tag not in tags]
            for tag in tags_not_specified:
                re_bbcode = re.compile(self.bbcode_rules[tag]['sub'][0], 
                                       re.MULTILINE|re.DOTALL|re.IGNORECASE)
                content = re_bbcode.sub(r'', content)
        return content     

    def get_media_tags(self):
        return [tag for (tag, value) in self.bbcode_rules.iteritems() if 'media' in value and value['media']]
