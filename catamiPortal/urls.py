from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'catamiPortal.views.home', name='home'),
    # url(r'^catamiPortal/', include('catamiPortal.foo.urls')),

    url(r'staging/', include('staging.urls')),

    #to hide the database name
    url(r'main/$','catamiPortal.views.index'),

    url(r'data/', include('Force.urls')),
    
    #haystack
    #(r'^search/', include('haystack.urls')),

    #to hide the database name
    #url(r'main/$','catamiPortal.views.index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
