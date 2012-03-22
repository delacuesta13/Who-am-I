# -*- coding: iso-8859-1 -*-

from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from itsme.models import Blog, Post, Project
from admin.views import blog_get_or_create

def index(request, page=1):
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    return render_to_response('itsme/index.html',
                              {
                               'user': user,
                               'blog': blog,
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
