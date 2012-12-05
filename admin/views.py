# -*- coding: iso-8859-1 -*-

import os
import re
from datetime import datetime
from time import strftime
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.validators import validate_email, validate_slug, URLValidator
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.template.defaultfilters import slugify, filesizeformat
from itsme.models import UserProfile, Upload, Category, Blog, Post, CategoryRelationships, Project
from itsme.bbcodeparser import BBCodeParser

"""
Important: 
set up in each view the var nav_active,
depending on item active in bar navigation.
"""

def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    #return render_to_response('admin/index.html', context_instance=RequestContext(request))
    return redirect('admin.views.post')

def extra_get_months():
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    return months

"""
Project
"""

def project(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    return render_to_response('admin/project/index.html',
                              {
                               'nav_active': 'work',
                               },
                              context_instance=RequestContext(request))

def project_list(request):
    """This view only loads if receive ajax request"""
    if request.is_ajax() and request.user.is_authenticated():
        
        # This will be used on project list template. 
        project_attr = [
                     {'attr': 'name', 'order_by': True, 'str': 'Name'},
                     {'attr': 'categories', 'order_by': False, 'str': 'Categories'},
                     {'attr': 'created_at', 'order_by': True, 'str': 'Date'},
                    ]
        # get attributes that allow order query
        order_attr = [attr['attr'] for attr in project_attr if attr['order_by']]
        
        projects = Project.objects.filter(user__id=request.user.id).order_by(*order_attr)        
        search, filter_by_search = '', False
        # 'order by' it orders the query by a specific attribute from model (column in db)
        order_by, order_by_att = '', False
        # 'order' it gives order (as ascendent and descendent) depending on the attribute
        order = ['asc', 'desc']
        page = 1
        
        # data received via get method
        if request.method == 'GET':
            # page
            if 'page' in request.GET:
                page = request.GET['page']
            # filter by search
            if ('search' in request.GET and
                len(request.GET['search']) > 0):
                search, filter_by_search = str(request.GET['search']), True
            # order by attribute
            if ('order_by' in request.GET and
                request.GET['order_by'].lower() in order_attr):
                order_by, order_by_att = request.GET['order_by'], True
                # get a copy of order_attr
                temp = order_attr[:]
                # remove from copy the order_by item
                temp.remove(order_by)
                if 'order' in request.GET and request.GET['order'].lower() in order:
                    order = request.GET['order'].lower()
                    if order == 'desc':
                        order_by = '-' + order_by
                else:
                    order = order[0]
                # create a new list
                order_attr = list()
                # add in new list order_by
                order_attr.append(order_by)
                # add in new list, old list without order_by item 
                order_attr += temp
            # set the custom query
            projects = Project.objects.filter(user__id=request.user.id,
                                        name__icontains=search).order_by(*order_attr)
            if not order_by_att:
                order_by, order = order_attr[0], order[0]
        else:
            # no data received
            order_by, order = order_attr[0], order[0]
            
        # remove hyphen if is ordering downward
        order_by = re.sub(r'^(-)(.+)$', r'\2', order_by)
        
        paginator = Paginator(projects, 10)
        
        # (num) page must be a integer
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # if query does not find records depending on (number) page, return records of last page 
        try:
            rs_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            rs_list = paginator.page(paginator.num_pages)
            
        # create a copy for highlight on search 
        object_list = list(rs_list.object_list)
           
        # highlight the search
        if filter_by_search:
            for i in xrange(len(object_list)):
                object_list[i].name = re.sub(r'(?i)(' + search + ')', r'<b>\1</b>', object_list[i].name)
                
        return render_to_response('admin/project/list.html',
                                  {
                                   'project_attr': project_attr,
                                   'projects_list': rs_list,
                                   'page': page,
                                   'search': search,
                                   'order_by': order_by,
                                   'order': order,
                                   },
                                  context_instance=RequestContext(request))
                                                         
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")
    
def project_edit(request, project_id = 0):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    mode = 'new'
    project = None
    
    if re.search(r'/work/edit/[0-9]+/$', request.path):
        try:
            project = Project.objects.get(id=project_id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            mode = 'edit'
    
    success_form, warning_form = False, False
    error_name, error_name_msg = False, ''
    error_slug, error_slug_msg = False, ''
    error_url, error_url_msg = False, ''
    
    project_categories = []
    
    # check if data received via post
    if (request.method == 'POST' and 'name' in request.POST
        and 'slug' in request.POST and 'description' in request.POST):
        # name
        name = request.POST['name']
        if not re.match(r'^.+$', name):
            error_name, error_name_msg = True, 'Please, enter a project name.'
            warning_form = True
        # slug
        slug = request.POST['slug']
        if re.match(r'^.+$', slug):
            try:
                validate_slug(slug)
            except ValidationError:
                error_slug, error_slug_msg = True, 'Please, enter a valid project slug.'
                warning_form = True
            else:
                if mode == 'new':
                    if Project.objects.filter(slug__iexact=slug).count() != 0:
                        error_slug, error_slug_msg = True, 'Already exists a project with same slug.'
                        warning_form = True
                else:
                    if Project.objects.exclude(id=project.id).filter(slug__iexact=slug).count() != 0:
                        error_slug, error_slug_msg = True, 'Already exists a project with same slug.'
                        warning_form = True
        else:
            error_slug, error_slug_msg = True, 'Please, enter a valid project slug.'
            warning_form = True
        # url
        site_url = request.POST['site_url']
        if re.match(r'^.+$', site_url):
            validate_url = URLValidator(verify_exists=True)
            try:
                validate_url(site_url)
            except ValidationError:
                error_url, error_url_msg = True, 'Enter a valid URL and verify that this one exists.'
                warning_form = True
        # continue if there are not errors
        if not warning_form:
            # create project object
            if mode == 'new':
                project = Project(user=request.user,
                                  name=name, slug=slug,
                                  site_url=site_url,
                                  description=request.POST['description'])
            else:
                # mode edit
                project.name = name
                project.slug = slug
                project.site_url = site_url
                project.description = request.POST['description']
            # save project object
            project.save()
            """ categories
            1. remove relationships between categories and the project
            2. save new relationships
            """
            project.categories.clear()
            for c in request.POST.getlist('categories[]'):
                project_categories.append(c)
                # save relationship
                try:
                    category = Category.objects.get(id=c)
                except ObjectDoesNotExist:
                    pass
                else:
                    associate = CategoryRelationships(category=category,
                                                      project=project)
                    associate.save()
            # redirect if a new project object has been created
            if mode == 'new':
                return redirect('admin.views.project_edit', project.id)
            else:
                success_form = True
                
    return render_to_response('admin/project/edit.html',
                              {
                               'mode': mode,
                               'project': project,
                               'project_categories': project_categories,
                               'categories': Category.objects.
                               filter(type_category__exact='work').order_by('name'),
                               'request': request,
                               'success_form': success_form,
                               'warning_form': warning_form,
                               'error_name': error_name, 'error_name_msg': error_name_msg,
                               'error_slug': error_slug, 'error_slug_msg': error_slug_msg,
                               'error_url': error_url, 'error_url_msg': error_url_msg,
                               'nav_active': 'work',
                               },
                              context_instance=RequestContext(request))
    
def post_preview(request, post_id):
    
    if not request.user.is_authenticated():
        return redirect('admin.views.login')
    
    post = get_object_or_404(Post, pk=post_id)
    
    content = BBCodeParser(post.content)
    content = content.bbcode_to_html(content.escape_html())
    
    return render_to_response('admin/preview/post.html',
                              {
                               'post': post,
                               'content': content,
                               'blog': blog_get_or_create(request.user),
                               'request': request,
                               },
                              context_instance=RequestContext(request))

def project_delete(request):
    if (request.user.is_authenticated() and request.is_ajax()
        and request.method == 'POST'):
        # save in a list the received ids
        id_list = request.POST.getlist('id[]')
        count_success = 0
        for id_project in id_list:
            try:
                count_success += 1
                project = Project.objects.get(pk=id_project)
                project.delete()
            except ObjectDoesNotExist:
                count_success -= 1
        return HttpResponse('<strong>Success!</strong> %d of %d rows selected have been deleted.' % (count_success, len(id_list)))
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")
    
"""
Post
"""

def post(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    return render_to_response('admin/post/index.html',
                              {
                               'nav_active': 'posts',
                               },
                              context_instance=RequestContext(request))

def post_list(request):
    """This view only loads if receive ajax request"""
    if request.is_ajax() and request.user.is_authenticated():
        
        # This will be used on posts list template. 
        # Like keys are unorganized in dictionaries,
        # use a list and add items depending on the
        # order to be shown.
        post_attr = [
                     {'attr': 'title', 'order_by': True, 'str': 'Title'},
                     {'attr': 'categories', 'order_by': False, 'str': 'Categories'},
                     {'attr': 'date', 'order_by': True, 'str': 'Date'},
                    ]
        # get attributes that allow order query
        order_attr = [attr['attr'] for attr in post_attr if attr['order_by']]
        
        posts = Post.objects.filter(blog__user__id=request.user.id).order_by(*order_attr)        
        search, filter_by_search = '', False
        # 'order by' it orders the query by a specific attribute from model (column in db)
        order_by, order_by_att = '', False
        # 'order' it gives order (as ascendent and descendent) depending on the attribute
        order = ['asc', 'desc']
        page = 1
        
        # data received via get method
        if request.method == 'GET':
            # page
            if 'page' in request.GET:
                page = request.GET['page']
            # filter by search
            if ('search' in request.GET and
                len(request.GET['search']) > 0):
                search, filter_by_search = str(request.GET['search']), True
            # order by attribute
            if ('order_by' in request.GET and
                request.GET['order_by'].lower() in order_attr):
                order_by, order_by_att = request.GET['order_by'], True
                # get a copy of order_attr
                temp = order_attr[:]
                # remove from copy the order_by item
                temp.remove(order_by)
                if 'order' in request.GET and request.GET['order'].lower() in order:
                    order = request.GET['order'].lower()
                    if order == 'desc':
                        order_by = '-' + order_by
                else:
                    order = order[0]
                # create a new list
                order_attr = list()
                # add in new list order_by
                order_attr.append(order_by)
                # add in new list, old list without order_by item 
                order_attr += temp
            # set the custom query
            posts = Post.objects.filter(blog__user__id=request.user.id,
                                        title__icontains=search).order_by(*order_attr)
            if not order_by_att:
                order_by, order = order_attr[0], order[0]
        else:
            # no data received
            order_by, order = order_attr[0], order[0]
            
        # remove hyphen if is ordering downward
        order_by = re.sub(r'^(-)(.+)$', r'\2', order_by)
        
        paginator = Paginator(posts, 10)
        
        # (num) page must be a integer
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # if query does not find records depending on (number) page, return records of last page 
        try:
            rs_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            rs_list = paginator.page(paginator.num_pages)
            
        # create a copy for highlight on search 
        object_list = list(rs_list.object_list)
           
        # highlight the search
        if filter_by_search:
            for i in xrange(len(object_list)):
                object_list[i].title = re.sub(r'(?i)(' + search + ')', r'<b>\1</b>', object_list[i].title)
                
        return render_to_response('admin/post/list.html',
                                  {
                                   'post_attr': post_attr,
                                   'posts_list': rs_list,
                                   'page': page,
                                   'search': search,
                                   'order_by': order_by,
                                   'order': order,
                                   },
                                  context_instance=RequestContext(request))
                                                         
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

def post_edit(request, post_id = 0):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    mode = 'new'
    post = None
    
    if re.search(r'/posts/edit/[0-9]+/$', request.path):
        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            raise Http404
        else:
            mode = 'edit'
            
    success_form = False
    warning_form = False
    error_title = False
    error_title_msg = ''         
    error_slug = False
    error_slug_msg = ''   
    
    post_categories = []      
            
    # check if data received via post
    if (request.method == 'POST' and 'title' in request.POST
        and 'slug' in request.POST and 'content' in request.POST):
        # title
        title = request.POST['title']
        if not re.match(r'^.+$', title):
            error_title, error_title_msg = True, 'Please, enter a post title.'
            warning_form = True
        # slug
        slug = request.POST['slug']
        if re.match(r'^.+$', slug):
            try:
                validate_slug(slug)
            except ValidationError:
                error_slug, error_slug_msg = True, 'Please, enter a valid post slug.'
                warning_form = True
            else:
                if mode == 'new':
                    if Post.objects.filter(slug__iexact=slug).count() != 0:
                        error_slug, error_slug_msg = True, 'Already exists a post with same slug.'
                        warning_form = True
                else:
                    if Post.objects.exclude(id=post.id).filter(slug__iexact=slug).count() != 0:
                        error_slug, error_slug_msg = True, 'Already exists a post with same slug.'
                        warning_form = True
        else:
            error_slug, error_slug_msg = True, 'Please, enter a valid post slug.'
            warning_form = True
        # continue if there are not errors
        if not warning_form:
            # create object Post
            if mode == 'new':
                post = Post(blog=blog_get_or_create(request.user),
                            content=request.POST['content'],
                            title=title, slug=slug)
            else:
                # mode edit
                post.title = title
                post.slug = slug
                post.content = request.POST['content']
            # date
            try:
                post.date = datetime(int(request.POST['year_date']), 
                                     int(request.POST['month_date']),
                                     int(request.POST['day_date']),
                                     int(request.POST['hour_date']),
                                     int(request.POST['minute_date']))
            except:
                post.date = datetime.now()
            # status
            if 'save' in request.POST:
                post.status = 'draft'
            elif 'publish' in request.POST:
                if post.date > datetime.now():
                    post.status = 'future'
                else:
                    post.status = 'publish'
            # save post
            post.save()
            """ categories
            1. remove relationships between categories and the post
            2. save new relationships
            """
            post.categories.clear()
            for c in request.POST.getlist('categories[]'):
                post_categories.append(c)
                # save relationship
                try:
                    category = Category.objects.get(id=c)
                except ObjectDoesNotExist:
                    pass
                else:
                    associate = CategoryRelationships(category=category,
                                                      post=post)
                    associate.save()
            # redirect if a new post object has been created
            if mode == 'new':
                return redirect('admin.views.post_edit', post.id)
            else:
                success_form = True
        
    return render_to_response('admin/post/edit.html',
                              {
                               'mode': mode,
                               'post': post,
                               'post_categories': post_categories,
                               'categories': Category.objects.
                               filter(type_category__exact='blog').order_by('name'),
                               'request': request,
                               'success_form': success_form,
                               'warning_form': warning_form,
                               'error_title': error_title,
                               'error_title_msg': error_title_msg,
                               'error_slug': error_slug,
                               'error_slug_msg': error_slug_msg,
                               'current_date': datetime.now(),
                               'months': extra_get_months(),
                               'nav_active': 'posts',
                               },
                              context_instance=RequestContext(request))

def post_delete(request):
    if (request.user.is_authenticated() and request.is_ajax()
        and request.method == 'POST'):
        # save in a list the received ids
        id_list = request.POST.getlist('id[]')
        count_success = 0
        for id_post in id_list:
            try:
                count_success += 1
                post = Post.objects.get(pk=id_post)
                post.delete()
            except ObjectDoesNotExist:
                count_success -= 1
        return HttpResponse('<strong>Success!</strong> %d of %d rows selected have been deleted.' % (count_success, len(id_list)))
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

"""
Blog
"""

def blog_get_or_create(user):
    try:
        blog = Blog.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        blog = Blog(user=user)
        blog.save()
    return blog

def blog_edit_settings(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    blog = blog_get_or_create(request.user)
    
    success_form = False
    
    if (request.method == 'POST' and 'site_title' in request.POST
        and 'tagline' in request.POST):
        blog.site_title = request.POST['site_title']
        blog.tagline = request.POST['tagline']
        blog.save()
        success_form = True
    
    return render_to_response('admin/blog/settings.html',
                              {
                               'nav_active': 'blog',
                               'blog': blog,
                               'success_form': success_form,
                               },
                              context_instance=RequestContext(request))

"""
Categories
"""

def category_get_types():
    """Return the types categories."""
    types_categories = {'work': 'Work', 'blog': 'Blog'}
    return types_categories

def category_get_slug(request):
    """Return a slug from string."""
    if (request.user.is_authenticated() and request.is_ajax() 
        and request.method == 'GET' and 'str' in request.GET):
        return HttpResponse(slugify(request.GET['str']))
    return HttpResponse("Oops! It's not possible respond your request :(")

def category_get_attributes(mode='list'):
    """Return a dict that contains attributes to order the category_list query, from category model."""
    if mode == 'dict':
        category_attributes = {'name': 'Name', 'type_category': 'Type', 'slug': 'Slug'}
    else:
        category_attributes = ['name', 'type_category', 'slug']
    return category_attributes

def category(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    return render_to_response('admin/category/index.html',
                              {
                               'nav_active': 'categories',
                               },
                              context_instance=RequestContext(request))

def category_list(request):
    """This view only loads if receive ajax request"""
    if request.is_ajax() and request.user.is_authenticated():
        
        categories = Category.objects.filter(user__id=request.user.id).order_by(*category_get_attributes())
        search, filter_by_search = '', False
        # 'order by' it orders the query by a specific attribute from model (column in db)
        order_by, order_by_search = category_get_attributes(), False
        # 'order' it gives order (as ascendent and descendent) depending on the attribute
        order = ['asc', 'desc']
        page = 1
        
        # data received via get method
        if request.method == 'GET':
            # page
            if 'page' in request.GET:
                page = request.GET['page']
            # filter by search
            if ('search' in request.GET and
                len(request.GET['search']) > 0):
                search, filter_by_search = str(request.GET['search']), True
            # order by attribute
            if ('order_by' in request.GET and
                request.GET['order_by'].lower() in order_by):
                temp = order_by
                order_by = temp.pop(temp.index(request.GET['order_by'].lower()))
                if 'order' in request.GET and request.GET['order'].lower() in order:
                    order = request.GET['order'].lower()
                    if order == 'desc':
                        order_by = '-' + order_by
                else:
                    order = order[0]
                # re-define attributes list
                temp_2 = order_by
                order_by = list()
                order_by.append(temp_2)
                order_by += temp 
                order_by_search = True
            # set the custom query
            categories = Category.objects.filter(user__id=request.user.id,
                                                 name__icontains=search).order_by(*order_by)
            if not order_by_search:
                order_by, order = order_by[0], order[0]
            else:
                order_by = temp_2
            # remove hyphen if is ordering downward
            order_by = re.sub(r'^(-)(.+)$', r'\2', order_by)
        else:
            # no data received
            order_by, order = order_by[0], order[0]
        
        paginator = Paginator(categories, 10)
        
        # (num) page must be a integer
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # if query does not find records depending on (number) page, return records of last page 
        try:
            rs_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            rs_list = paginator.page(paginator.num_pages)
            
        # create a copy for highlight on search 
        object_list = list(rs_list.object_list)
           
        # highlight the search
        if filter_by_search:
            for i in xrange(len(object_list)):
                object_list[i].name = re.sub(r'(?i)(' + search + ')', r'<b>\1</b>', object_list[i].name)
                
        return render_to_response('admin/category/list.html',
                                  {
                                   'categories_list': rs_list,
                                   'page': page,
                                   'search': search,
                                   'order_by': order_by,
                                   'order': order,
                                   'cols_query': category_get_attributes('dict'),
                                   'categories_types': category_get_types(),
                                   },
                                  context_instance=RequestContext(request))
                                                         
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

def category_add(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    warning_form = False
    error_name = False
    error_name_msg = ''
    error_type = False
    error_type_msg = ''
    error_slug = False
    error_slug_msg = ''
    
    if (request.method == "POST" and 'name' in request.POST
        and 'type' in request.POST and 'slug' in request.POST):
        name_cat = request.POST['name']
        type_cat = request.POST['type']
        slug_cat = request.POST['slug']
        if re.match(r'^.+$', name_cat) and type_cat in category_get_types():
            # validate slug field
            try:
                validate_slug(slug_cat)
            except ValidationError:
                error_slug, error_slug_msg = True, 'Enter a correct category slug.'
                warning_form = True 
            else:
                count_name = Category.objects.filter(user__id=request.user.id,
                                                     type_category=type_cat,
                                                     name__iexact=name_cat).count()
                if count_name == 0:
                    count_slug = Category.objects.filter(user__id=request.user.id,
                                                         type_category=type_cat,
                                                         slug__iexact=slug_cat).count()
                    if count_slug == 0:
                        c = Category(user=request.user,
                                     name=name_cat,
                                     slug=slug_cat,
                                     type_category=type_cat,
                                     description=request.POST['description'])
                        c.save()
                        return redirect('admin.views.category_edit', c.id)
                    else:
                        error_slug, error_slug_msg = True, 'Already exists a category with same slug.'
                        warning_form = True
                else:
                    error_name, error_name_msg = True, 'Already exists a category with same name.'
                    warning_form = True 
        else:
            if not re.match(r'^.+$', name_cat):
                error_name, error_name_msg = True, 'Please, enter a category name.'
                warning_form = True
            if type_cat not in category_get_types():
                error_type, error_type_msg = True, 'Please, select a category type.'
                warning_form = True 
    
    return render_to_response('admin/category/edit.html',
                              {
                               'warning_form': warning_form,
                               'error_name': error_name,
                               'error_name_msg': error_name_msg,
                               'error_type': error_type,
                               'error_type_msg': error_type_msg,
                               'error_slug': error_slug,
                               'error_slug_msg': error_slug_msg, 
                               'request': request,
                               'types_categories': category_get_types(),
                               'nav_active': 'categories',
                               },
                              context_instance=RequestContext(request))

def category_edit(request, category_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    category = get_object_or_404(Category, pk=category_id)
    
    # only edit if user is who created the category
    if category.user.id != request.user.id:
        raise Http404
    
    success_form = False
    warning_form = False
    error_name = False
    error_name_msg = ''
    error_type = False
    error_type_msg = ''
    error_slug = False
    error_slug_msg = ''
    
    if (request.method == "POST" and 'name' in request.POST
        and 'type' in request.POST and 'slug' in request.POST):
        name_cat = request.POST['name']
        type_cat = request.POST['type']
        slug_cat = request.POST['slug']
        if re.match(r'^.+$', name_cat) and type_cat in category_get_types():
            # validate slug field
            try:
                validate_slug(slug_cat)
            except ValidationError:
                error_slug, error_slug_msg = True, 'Enter a correct category slug.'
                warning_form = True 
            else:
                count_name = Category.objects.filter(user__id=request.user.id,
                                                     type_category=type_cat,
                                                     name__iexact=name_cat).exclude(pk=category.id).count()
                if count_name == 0:
                    count_slug = Category.objects.filter(user__id=request.user.id,
                                                         type_category=type_cat,
                                                         slug__iexact=slug_cat).exclude(pk=category.id).count()
                    if count_slug == 0:
                        category.name = name_cat
                        category.slug = slug_cat
                        category.type_category = type_cat
                        category.description = request.POST['description']
                        category.save()
                        success_form = True
                    else:
                        error_slug, error_slug_msg = True, 'Already exists a category with same slug.'
                        warning_form = True
                else:
                    error_name, error_name_msg = True, 'Already exists a category with same name.'
                    warning_form = True 
        else:
            if not re.match(r'^.+$', name_cat):
                error_name, error_name_msg = True, 'Please, enter a category name.'
                warning_form = True
            if type_cat not in category_get_types():
                error_type, error_type_msg = True, 'Please, select a category type.'
                warning_form = True
    
    return render_to_response('admin/category/edit.html',
                              {
                               'category': category,
                               'success_form': success_form,
                               'warning_form': warning_form,
                               'error_name': error_name,
                               'error_name_msg': error_name_msg,
                               'error_type': error_type,
                               'error_type_msg': error_type_msg,
                               'error_slug': error_slug,
                               'error_slug_msg': error_slug_msg, 
                               'request': request,
                               'types_categories': category_get_types(),
                               'mode': 'edit',
                               'nav_active': 'categories',
                               },
                              context_instance=RequestContext(request))

def category_delete(request):
    if (request.user.is_authenticated() and request.is_ajax()
        and request.method == 'POST'):
        # save in a list the received ids
        id_list = request.POST.getlist('id[]')
        count_success = 0
        for id_category in id_list:
            try:
                count_success += 1
                c = Category.objects.get(pk=id_category)
                c.delete()
            except ObjectDoesNotExist:
                count_success -= 1
        return HttpResponse('<strong>Success!</strong> %d of %d rows selected have been deleted.' % (count_success, len(id_list)))
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

"""
Media
"""

def media(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    return render_to_response('admin/media/index.html',
                              {
                               'nav_active': 'media',
                               },
                              context_instance=RequestContext(request))

def media_list(request):
    """This view only loads if receive ajax request"""
    if request.user.is_authenticated() and request.is_ajax():
        
        media = Upload.objects.filter(user__id=request.user.id).order_by('-upload_date', 'title')
        search, filter_by_search = '', False
        page = 1
        
        # check if received data are of request type 'GET' 
        if request.method == 'GET':
            if 'page' in request.GET:
                page = request.GET['page']
            if 'search' in request.GET and len(request.GET['search'])>0:
                search = str(request.GET["search"])
                media = Upload.objects.filter(user__id=request.user.id, title__icontains=search).order_by('-upload_date', 'title')
                filter_by_search = True    
            
        paginator = Paginator(media, 10)
        
        # (num) page must be a integer
        try:
            page = int(page)
        except ValueError:
            page = 1
        
        # if query does not find records depending on (number) page, return records of last page 
        try:
            rs_list = paginator.page(page)
        except (EmptyPage, InvalidPage):
            rs_list = paginator.page(paginator.num_pages)
            
        # create a copy for highlight on search 
        object_list = list(rs_list.object_list)
            
        # highlight the search
        if filter_by_search:
            for i in xrange(len(object_list)):
                object_list[i].title = re.sub(r'(?i)(' + search + ')', r'<b>\1</b>', object_list[i].title) 
                
        return render_to_response('admin/media/list.html',
                                  {
                                   'media_list': rs_list,
                                   'page': page,
                                   'search': search,
                                   },
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

def media_add(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    warning_form = False
    error_upfile = False
    msg_error_upfile = ''
    
    # regular expressions
    fname_pattern = re.compile(r'^.+$')
    fext_allowed = ['jpg', 'gif', 'png']
    
    # check if data was received
    if request.method == "POST":
        # check if file was uploaded
        if 'file' in request.FILES:
            upfile = request.FILES['file']
            """
            file size (in bytes) must be less or equal than allowed maximum
            default: 2621440 bytes (2.5 MB)
            """
            if upfile.size <= settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                # file name
                name_upfile = re.sub(r'(.+)(\.\w+)', r'\1', upfile.name)
                # file extension o format
                ext_upfile = os.path.splitext(upfile.name)[1].lower()
                # remove the starting point
                ext_upfile = ext_upfile[1:]
                # only extensions defined in fext_pattern and a file name correct
                if fname_pattern.match(name_upfile) and ext_upfile in fext_allowed:
                    """
                    check if exist a same name file in absolute path where save it.
                    only characters allowed for file name
                    """
                    temp_fname = slugify(name_upfile)
                    absolute_path = settings.MEDIA_ROOT
                    absolute_path += 'uploads/images/%d/%s/%s/%s.%s' % (request.user.id, strftime('%Y'), strftime('%m'), temp_fname, ext_upfile)
                    if not os.path.exists(absolute_path):
                        """
                        make dir for user, if it doesn't exist
                        and make subs dir depending on year and month.
                        
                        directory structure for save user images:
                        uploads/images/user_id/year/month/filename
                        
                        For save the images, see:
                        http://stackoverflow.com/questions/3702465/how-to-copy-inmemoryuploadedfile-object-to-disk
                        """
                        # make dir uploads
                        user_dir = settings.MEDIA_ROOT + 'uploads'
                        if not os.path.exists(user_dir):
                            os.mkdir(user_dir, settings.FILE_UPLOAD_PERMISSIONS)
                        # make dir images
                        user_dir = '%s/images' % user_dir
                        if not os.path.exists(user_dir):
                            os.mkdir(user_dir, settings.FILE_UPLOAD_PERMISSIONS)
                        # make dir for user
                        user_dir = '%s/%d' % (user_dir,request.user.id)
                        if not os.path.exists(user_dir):
                            os.mkdir(user_dir, settings.FILE_UPLOAD_PERMISSIONS)
                        # make dir depending on current year
                        user_dir = '%s/%s' % (user_dir, strftime('%Y'))
                        if not os.path.exists(user_dir):
                            os.mkdir(user_dir, settings.FILE_UPLOAD_PERMISSIONS)
                        # make dir depending on current month
                        user_dir = '%s/%s' % (user_dir, strftime('%m'))
                        if not os.path.exists(user_dir):
                            os.mkdir(user_dir, settings.FILE_UPLOAD_PERMISSIONS)
                        file_dir = '%s/%s' % (user_dir, '%s.%s' % (temp_fname, ext_upfile))
                        default_storage.save(file_dir, ContentFile(upfile.read()))
                        # save the image uploaded
                        absolute_path = 'uploads/images/%d/%s/%s/%s.%s' % (request.user.id,strftime('%Y'),strftime('%m'),temp_fname, ext_upfile)
                        up = Upload(path=absolute_path, title=name_upfile, extension_file=upfile.content_type, user=request.user)
                        up.save()
                        return redirect('admin.views.media_edit', upload_id=up.pk)
                    else:
                        warning_form = True
                        error_upfile = True
                        msg_error_upfile = 'Already exists a file with the same name file for upload.' 
                else:
                    warning_form = True
                    error_upfile = True
                    msg_error_upfile = 'Please, upload a file with a valid extension (<strong>%s</strong>).' % ', '.join(fext_allowed)
            else:
                warning_form = True
                error_upfile = True
                # convert to MB
                msg_error_upfile = 'The maximum file size is %s.' % filesizeformat(settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
        else:
            warning_form = True
            error_upfile = True
            msg_error_upfile = 'Please, select a file for upload.'
        
    return render_to_response('admin/media/add.html',
                              {
                               'warning_form': warning_form,
                               'error_upfile': error_upfile,
                               'msg_error_upfile': msg_error_upfile,
                               'nav_active': 'media',
                               }, 
                              context_instance=RequestContext(request))

def media_edit(request, upload_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    up = get_object_or_404(Upload, pk=upload_id)
    # only allow edit upload if user in session is same user than uploaded the file
    if up.user.id != request.user.id:
        raise Http404

    dir_file = str(settings.MEDIA_ROOT + up.path)
    fd = open(dir_file)
    img =  ImageFile(fd)
    # get filename without path
    img.name_notpath = os.path.basename(dir_file)
    
    success_edit = False
    warning_edit = False
    error_name = False
    
    if request.method == "POST":
        if re.match(r'^.+$', request.POST['name']):
            up.title = request.POST['name']
            up.description = request.POST['description']
            up.save()
            success_edit = True
        else:
            error_name = True
            warning_edit = True
    
    return render_to_response('admin/media/edit.html', 
                              {
                               'upload': up,
                               'img': img,
                               'success_edit': success_edit,
                               'warning_edit': warning_edit,
                               'error_name': error_name,
                               'request': request,
                               'nav_active': 'media',
                               },
                              context_instance=RequestContext(request))

def media_delete(request):
    if (request.user.is_authenticated() and request.is_ajax()
        and request.method == 'POST'):
        # save in a list the received ids
        id_list = request.POST.getlist('id[]')
        count_success = 0
        for id_upload in id_list:
            try:
                count_success += 1
                u = Upload.objects.get(pk=id_upload)
                try:
                    os.remove(settings.MEDIA_ROOT + u.path)
                except OSError:
                    count_success -= 1
                else:
                    u.delete()
            except ObjectDoesNotExist:
                count_success -= 1
        return HttpResponse('<strong>Success!</strong> %d of %d rows selected have been deleted.' % (count_success, len(id_list)))
    else:
        return HttpResponse("Oops! It's not possible respond your request :(")

"""
Edit data from profile
"""

def profile_get_or_create(user):
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()
    return profile

def profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    return render_to_response('admin/profile.html',
                              {
                               'nav_active': 'profile',
                               'active_tab': 'profile',
                               }, 
                              context_instance=RequestContext(request))

def profile_info_edit(request): 
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    success_info = False
    warning_info = False
    error_fname = False
    error_lname = False
    error_email = False
    error_phone = False
    
    # regular expressions 
    name_pattern = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚ\s]*$')
    phone_pattern = re.compile(r'^(\+?\d+\s?)?(\(\d+\)\s?|\d+\s?)?\d*$')
    
    if request.method != "POST":
        return HttpResponseRedirect(reverse('admin.views.profile'))
    else:
        # validate email
        email = request.POST["email"]
        if len(email) > 0:
            try:
                validate_email(email)
            except ValidationError:
                error_email = True
                warning_info = True
        # validate first name
        first_name = request.POST["first_name"]
        if not name_pattern.match(first_name):
            error_fname = True
            warning_info = True
        # validate last name
        last_name = request.POST["last_name"]
        if not name_pattern.match(last_name):
            error_lname = True
            warning_info = True
        # validate phone
        phone = request.POST["phone"]
        if not phone_pattern.search(phone):
            error_phone = True
            warning_info = True
        
        location = request.POST["location"]
        # no errors were found
        if not warning_info:
            u = request.user
            u.first_name = first_name
            u.last_name = last_name
            u.email = email
            profile = profile_get_or_create(u)
            profile.phone = phone
            profile.location = location
            profile.save()
            u.save()
            success_info = True
    
    return render_to_response('admin/profile.html', 
                              {
                               'success_info': success_info,
                               'warning_info': warning_info,
                               'error_fname': error_fname,
                               'error_lname': error_lname,
                               'error_email': error_email,
                               'error_phone': error_phone,
                               'request': request,
                               'nav_active': 'profile',
                               },
                              context_instance=RequestContext(request))

def profile_edit(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    success_profile = False
    
    if request.method != "POST":
        return HttpResponseRedirect(reverse('admin.views.profile'))
    else:
        profile = profile_get_or_create(request.user)
        profile.profession = request.POST["profession"]
        profile.about = request.POST["about"]
        profile.resume = request.POST["resume"]
        profile.save()
        success_profile = True
        
    return render_to_response('admin/profile.html', 
                              {
                               'success_profile': success_profile,
                               'nav_active': 'profile',
                               'active_tab': 'profile',
                               },
                              context_instance=RequestContext(request))
    
def profile_password_edit(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.login'))
    
    success_pass = False
    warning_pass = False
    error_opass = False
    error_npass = False
    error_cpass = False
    
    if request.method != "POST":
        return HttpResponseRedirect(reverse('admin.views.profile'))
    else:
        # get data received
        old_pass = request.POST["old_pass"]
        new_pass = request.POST["new_pass"]
        confirm_pass = request.POST["confirm_pass"]
        # check old password
        if (len(old_pass) > 0 and request.user.check_password(old_pass) 
            and len(new_pass) > 0 and new_pass == confirm_pass):
            request.user.set_password(new_pass)
            request.user.save()
            success_pass = True
        else:
            if len(old_pass) == 0 or not request.user.check_password(old_pass): 
                warning_pass, error_opass = True, True
            if len(new_pass) == 0 or new_pass != confirm_pass:
                warning_pass, error_npass, error_cpass = True, True, True
    
    return render_to_response('admin/profile.html', 
                              {
                               'success_pass': success_pass,
                               'warning_pass': warning_pass,
                               'error_opass': error_opass,
                               'error_npass': error_npass,
                               'error_cpass': error_cpass,
                               'nav_active': 'profile',
                               'active_tab': 'password',
                               },
                              context_instance=RequestContext(request)) 

"""
Login and logout
"""

def login(request):
    error_login = False
    error_message = 'Username and password are incorrect.'
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('admin.views.index'))
    elif request.method == "POST":
        # check data received
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            # authenticate given username and password 
            user = authenticate(username=username, password=password)
            # success
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return HttpResponseRedirect(reverse('admin.views.index'))
                else:
                    error_message = 'Your account user is not active.'
            else:
                error_login = True
        else: 
            error_login = True
            
    return render_to_response('admin/login.html', 
                              {
                               'error_login': error_login,
                               'error_message': error_message,
                               'request': request
                               },
                              context_instance=RequestContext(request))

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('admin.views.login'))