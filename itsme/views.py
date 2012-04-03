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
from itsme.models import Post, Project
from admin.views import blog_get_or_create
from itsme.bbcodeparser import BBCodeParser

def index(request, page=1):
    
    if re.match(r'^/page/1/$', request.path):
        return redirect('/', permanent=True)
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    post_set_to_publish()
    
    post_list = Post.objects.filter(blog__id=blog.id,
                                    status__iexact='publish').order_by('-date', 'title')
    
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

def post_view(request, slug):
    
    try:
        post = Post.objects.get(slug__exact=slug,
                                status__exact='publish')
    except ObjectDoesNotExist:
        raise Http404
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    post_content = BBCodeParser(post.content)
    content = post_content.bbcode_to_html(post_content.escape_html())
    
    previous_post = Post.objects.exclude(slug__exact=post.slug).filter(date__lte=post.date).order_by('-date', 'title').count()
    if previous_post > 0:
        previous_post = Post.objects.exclude(slug__exact=post.slug).filter(date__lte=post.date).order_by('-date', 'title')[0]
    else:
        previous_post = False
    next_post = Post.objects.exclude(slug__exact=post.slug).filter(date__gte=post.date).order_by('date', 'title').count()
    if next_post > 0:
        next_post = Post.objects.exclude(slug__exact=post.slug).filter(date__gte=post.date).order_by('date', 'title')[0]
    else:
        next_post = False
    
    return render_to_response('itsme/post_view.html',
                              {
                               'post': post,
                               'user': user,
                               'blog': blog,
                               'post_content': post_content,
                               'content': content,
                               'previous_post': previous_post,
                               'next_post': next_post,
                               },
                              context_instance=RequestContext(request))

def post_set_to_publish():
    """Set future articles as published articles, if their date is less or equal to current date."""
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    current_date = datetime.now()
    
    Post.objects.filter(date__lte=current_date,
                        status__iexact='future',
                        blog__id=blog.id).update(status='publish')

"""
Work
"""

def work(request):
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    projects = Project.objects.all().order_by('-created_at', 'name') 
    
    return render_to_response('itsme/work.html',
                              {
                               'user': user,
                               'blog': blog,
                               'projects': projects,
                               'nav_active': 'work',
                               },
                              context_instance=RequestContext(request))

"""
About
"""

def about(request):
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    resume = BBCodeParser(user.get_profile().resume)
    resume = resume.bbcode_to_html(resume.escape_html())
    
    return render_to_response('itsme/about.html',
                              {
                               'user': user,
                               'blog': blog,
                               'resume': resume,
                               'nav_active': 'about',
                               },
                              context_instance=RequestContext(request))

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
