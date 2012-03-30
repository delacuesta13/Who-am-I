# -*- coding: iso-8859-1 -*-

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
#from django.template.defaultfilters import force_escape
from itsme.bbcodeparser import BBCodeParser
from itsme.models import Post
from itsme.views import user_get_owner, post_set_to_publish
from admin.views import blog_get_or_create

class RSSFeed(Feed):
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    feed_type = feedgenerator.Rss201rev2Feed
    
    def title(self):
        s = self.blog.site_title if len(self.blog.site_title) > 0 else self.user.get_full_name()
        return '%s' % s
    
    def link(self):
        return '%s' % settings.BASE_URL
    
    def feed_url(self):
        return '%s/feed/' % settings.BASE_URL
    
    def description(self):
        return 'Updates of articles about Internet, Software Development, free and open technologies and other things.'
    
    def items(self):
        post_set_to_publish()
        return Post.objects.filter(status__iexact='publish').order_by('-date', 'title')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        bbcode_parser = BBCodeParser(item.content)
        if len(bbcode_parser.get_all_paragraphs()) > 0:
            s = bbcode_parser.remove_bbcode(bbcode_parser.get_all_paragraphs()[0])
        else:
            s = 'This article doesn\'t have description.'
        return s
    
    def item_link(self, item):
        return '/blog/%s/' % item.slug
    
    def item_author_name(self, item):
        return item.blog.user.get_full_name()
    
    def item_pubdate(self, item):
        return item.date
    
    def item_categories(self, item):
        return item.categories.all()
    
    def get_feed(self, obj, request):
        """Set mime type of request.
        
        Originally taked from:
        originally tommed from http://opensrc.mx/post/12642801896/cambiar-el-mimetype-feed-de-django-para-que-en-chrome"""
        f = super(RSSFeed,self).get_feed(obj,request) 
        f.mime_type="application/xml"
        return f
        