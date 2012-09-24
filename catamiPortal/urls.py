from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'catamiPortal.views.home', name='home'),
    # url(r'^catamiPortal/', include('catamiPortal.foo.urls')),

    url(r'staging/', include('staging.urls')),

    url(r'main/', include('Force.urls')),

    #to hide the database name
    url(r'^main/$','catamiPortal.views.index'),
    
    #views
    #url(r'^main/auvdeployments/$', 'Force.views.auvdeployments'),
    #url(r'^main/campaigns/$', 'Force.views.campaigns'),
    #url(r'^main/campaigns/(?P<campaign_id>\d+)/$', 'Force.views.campaignDetail'),
    #url(r'^main/auvdeployments/(?P<auvdeployment_id>\d+)/$', 'Force.views.auvdeploymentDetail'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
