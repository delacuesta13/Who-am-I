from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/', include('admin.urls')),
    url(r'^$', 'itsme.views.index'),
    url(r'^page/(?P<page>\d+)/$', 'itsme.views.index'),
    url(r'^blog/(?P<slug>[\w-]+)/$', 'itsme.views.post_view')
)