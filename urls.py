from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/', include('admin.urls')),
    url(r'^$', 'itsme.views.index'),
)