# -*- coding: iso-8859-1 -*-

from datetime import datetime
import re
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.paginator import Paginator, InvalidPage, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.template import RequestContext
from django.http import Http404
from django.shortcuts import redirect, render_to_response
from itsme.models import Post, Project, Message
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
Contact
"""

def contact(request):
    
    user = user_get_owner()
    blog = blog_get_or_create(user)
    
    warning_form = False
    success_form = False
    error_form, error_form_msg = False, ''
    
    error_name, error_name_msg = False, ''
    error_email, error_email_msg = False, ''
    error_message, error_message_msg = False, '' 
    
    if (request.method == 'POST' and 'name' in request.POST
        and 'email' in request.POST and 'message' in request.POST):
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        
        if not re.match('^.+$', name):
            error_name, error_name_msg = True, 'Please, enter your name.'
            warning_form = True
            
        try:
            validate_email(email)
        except ValidationError:
            error_email, error_email_msg = True, 'Please, enter a valid e-mail address.'      
            warning_form = True     
            
        if len(message) == 0:
            error_message, error_message_msg = True, 'Please, write a message for i reply you.'      
            warning_form = True 
            
        # get (separated) current year, month and day
        year, month, day = datetime.now().strftime('%Y %m %d').split(' ')
        today_start = datetime(int(year), int(month), int(day), 0, 0 , 0)
        today_end = datetime(int(year), int(month), int(day), 23, 59 , 59)
        
        # get number of messages from email address today
        num_max_messages_for_day = 3
        # number of messages by email
        num_messages_today_email = Message.objects.filter(email__iexact=email, 
                                              date__gte=today_start,
                                              date__lte=today_end).count()
        # number of messages by ip address
        num_messages_today_ip = Message.objects.filter(ip__iexact=request.META['REMOTE_ADDR'], 
                                              date__gte=today_start,
                                              date__lte=today_end).count()
                                              
        # check if a same email address is sending multiple messages
        if (num_messages_today_email >= num_max_messages_for_day
            or num_messages_today_ip >= num_max_messages_for_day):
            error_form = True
            error_form_msg = 'You have sent %d messages today, maximum number allowed.' % num_max_messages_for_day
        
        if not warning_form and not error_form:
            msg = Message(user=user, ip=request.META['REMOTE_ADDR'], 
                          author=name, email=email, content=message)
            msg.save()
            success_form = True
        
    return render_to_response('itsme/contact.html',
                              {
                               'user': user,
                               'blog': blog,
                               'request': request,
                               'warning_form': warning_form,
                               'success_form': success_form,
                               'error_form': error_form, 'error_form_msg': error_form_msg,
                               'error_name': error_name, 'error_name_msg': error_name_msg,
                               'error_email': error_email, 'error_email_msg': error_email_msg,
                               'error_message': error_message, 'error_message_msg': error_message_msg,
                               'nav_active': 'contact',
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
