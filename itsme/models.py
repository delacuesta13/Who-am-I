from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True) # quick overview
    resume = models.TextField(blank=True) # complete overview
    available_for_work = models.BooleanField(default=True)
    
class Blog(models.Model):
    user = models.ForeignKey(User, unique=True)
    site_title = models.CharField(max_length=100, blank=True)
    tagline = models.CharField(max_length=100, blank=True)
    
    def __unicode__(self):
        return self.site_title

class Category(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    type_category_choices = (
        ('work', 'Work'),
        ('blog', 'Blog'),
    )
    type_category = models.CharField(max_length=16, choices=type_category_choices)
    
    def __unicode__(self):
        return self.name
    
class Post(models.Model):
    blog = models.ForeignKey(Blog)
    categories = models.ManyToManyField(Category, through='CategoryRelationships')
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
    title = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    content = models.TextField(blank=True)
    status_choices = (
        ('publish', 'Publish'),  
        ('draft', 'Draft'),
        ('future', 'Schedule'),                  
    )
    status = models.CharField(max_length=16, choices=status_choices, default="publish")
    allow_comments = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True, auto_now_add=False)
    
    def __unicode__(self):
        return self.title
    
    def get_status(self):
        status = self.status.lower()
        if status == 'draft': 
            status = status.capitalize()
        elif status == 'publish':
            status = 'Published'
        elif status == 'future': 
            status = 'Schudeled'   
        return status
        
class Comment(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    author = models.CharField(max_length=30)
    email = models.EmailField(max_length=100)
    url = models.URLField(blank=True)
    ip = models.IPAddressField(max_length=100)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    content = models.TextField()
    is_moderate = models.BooleanField(default=False)
    is_safe = models.BooleanField(default=False) # if True, allow HTML code
    
class Project(models.Model):
    user = models.ForeignKey(User)
    categories = models.ManyToManyField(Category, through='CategoryRelationships')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    site_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True, auto_now_add=False)
    
    def __unicode_(self):
        return self.name
    
class CategoryRelationships(models.Model):
    category = models.ForeignKey(Category)
    post = models.ForeignKey(Post, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    
class Message(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    ip = models.IPAddressField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)    
    is_readed = models.BooleanField(default=False)

class Upload(models.Model):
    user = models.ForeignKey(User)
    path = models.TextField(blank=True)
    title = models.TextField(blank=True)
    upload_date = models.DateTimeField(null=True, auto_now=False, auto_now_add=True)
    extension_file = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
