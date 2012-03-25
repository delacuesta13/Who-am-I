# -*- coding: iso-8859-1 -*-

import re

class BBCodeParser:

    bbcode_rules = {
            'heading': {
                        'sub': [r'\[h([1-6]{1})\](.*?)\[/h([1-6]{1})\]',
                                r'<h\1>\2</h\1>', r'\2'],
                        },
            'paragraph': {
                          'sub': [r'\[p\](.*?)\[/p\]', r'<p>\1</p>', r'\1'],
                          'findall': r'\[p\](.*?)\[/p\]'
                          },
            'color': {
                      'sub': [r'\[color=(#[0-9a-fA-F]{3,6}|[a-zA-Z]+)\](.*?)\[/color\]',
                              r'<span style="color: \1;">\2</span>', r''], 
                      },
            'size': {
                     'sub': [r'\[size=(\d+)\](.*?)\[/size\]',
                             r'<span style="font-size: \1px;">\2</span>',
                             r''],
                     },
            'bold': {
                     'sub': [r'\[b\](.*?)\[/b\]', r'<strong>\1</strong>',
                             r'\1'],
                     },
            'italic': {
                       'sub': [r'\[i\](.*?)\[/i\]', r'<em>\1</em>',
                               r'\1'],
                       },
            'Stroke through': {
                               'sub': [r'\[del\](.*?)\[/del\]', r'<del>\1</del>',
                                       r'\1'],
                               },
            'link': {
                     'sub': [r'\[url=(.*?)\](.+?)\[/url\]', r'<a href="\1">\2</a>',
                             r'\2'],
                     },
            'youtube': {
                        'sub': [r'\[youtube\s+width=(\d*?)\s+height=(\d*?)\](.*?)\[/youtube\]',
                                r'<div class="video-container"><iframe width="\1" height="\2" src="http://www.youtube.com/embed/\3" frameborder="0"></iframe></div>',
                                r''],
                        },
            'vimeo': {
                      'sub': [r'\[vimeo\s+width=(\d*?)\s+height=(\d*?)\](.*?)\[/vimeo\]',
                              r'<div class="video-container"><iframe src="http://player.vimeo.com/video/\3?byline=0&amp;portrait=0&amp;color=707070" width="\1" height="\2" frameborder="0"></iframe><div>',
                              r'']
                      },        
    }
    
    def __init__(self, bbcode):
        self.bbcode = bbcode
        
    def bbcode_to_html(self):
        s = self.bbcode
        for value in self.bbcode_rules.itervalues():
            re_bbcode = re.compile(value['sub'][0], re.MULTILINE|re.DOTALL|re.IGNORECASE) 
            s = re_bbcode.sub(value['sub'][1], s)
        return s

    def get_all_paragraphs(self):
        return re.findall(self.bbcode_rules['paragraph']['findall'], self.bbcode)
    
    def remove_bbcode(self, s, *tags):
        without_bbcode = s
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
        