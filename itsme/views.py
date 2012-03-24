# -*- coding: iso-8859-1 -*-

from datetime import datetime
import re
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.paginator import Paginator, InvalidPage, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from itsme.models import Blog, Post, Project
from admin.views import blog_get_or_create

def index(request, page=1):
    
    if re.match('^/page/1/$', request.path):
        return redirect('/', permanent=True)
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    current_date = datetime.now()
    
    # update notes if their status are 'future' and their date 
    # is less than current date
    Post.objects.filter(date__lte=current_date,
                        status__iexact='future',
                        blog__id=blog.id).update(status='publish')
    
    post_list = Post.objects.filter(blog__id=blog.id,
                                    status='publish').order_by('-date', 'title')
    
    paginator = Paginator(post_list, 5)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except (EmptyPage, InvalidPage):
        posts = paginator.page(paginator.num_pages)
    
    return render_to_response('itsme/index.html',
                              {
                               'user': user,
                               'blog': blog,
                               'posts': posts,
                               },
                              context_instance=RequestContext(request))

"""
Post
"""

def post_view(request, post_slug):
    pass

"""
get owner user of site
"""

def user_get_owner():
    """Return owner user object of site."""
    try:
        user_email = settings.ADMINS[0][1]
        user = User.objects.get(email__exact=user_email)
    except:
        user = User.objects.latest('date_joined')
    return user
