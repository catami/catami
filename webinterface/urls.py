"""URL Mappings for the webinterface application.
"""
from catamidb import authorization
from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin
from django.views.generic.simple import direct_to_template


admin.autodiscover()

#configure initial auth and groups
authorization.on_startup_configuration()

urlpatterns = patterns(
    'webinterface.views',
    url(r'^$', 'index', name='index'),

    #Info Pages
    url(r'^faq', 'faq'),
    url(r'^contact', 'contact'),
    url(r'^licensing', 'licensing'),
    url(r'^howto', 'howto'),
    url(r'^about', 'about'),
    url(r'^proxy/$', 'proxy'),



    #url(r'^viewcollection$', 'viewcollection'),

    #Staging
    #url(r'^staging/', include('staging.urls')),
    # campaign creating
    url(r'^staging/campaign/create$', 'campaigncreate',
                           name='staging_campaign_create'),
   
    # Projects
    #url(r'^projects$', 'projects'),
    url(r'^projects/$', 'projects'),
    url(r'^projects/(?P<project_id>\d+)/$', 'project_view'),
    url(r'^projects/(?P<project_id>\d+)/configure/$', 'project_configure'),
    url(r'^projects/(?P<project_id>\d+)/configure/(?P<annotation_set_id>\d+)/$', 'project_annotate'),


    #plain data views
    url(r'^data/$', 'data'),
    url(r'^data/deployments/$', 'deployments'),
    url(r'^data/deployments/(?P<deployment_id>\d+)/$',
        'deployment_detail'),
    url(r'^data/campaigns/$', 'campaigns'),
    url(r'^data/campaigns/(?P<campaign_id>\d+)/$',
        'campaign_detail'),

    #API docs
    url(r'^api/', include('jsonapi.urls')),

    #dbadmin tool
    #url(r'^report/', include('dbadmintool.urls')),

    # userena
    (r'^accounts/', include('accounts.urls')),
    url(r'^logout/$', 'logout_view'),

    #admin interface
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns(
    '',
    url(r'^accounts/login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'}),
    # the raw original images
    url(r'images/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.IMAGES_ROOT, 'show_indexes': True}),
    # url(r'^{0}/(?P<path>.*)$'.format(settings.IMAGES_URL),
    #     'django.views.static.serve',
    #     {'document_root': settings.IMAGES_ROOT,
    #      'show_indexes': False}),
    # and the thumbnails...
    #url(r'^thumbnails/', include('restthumbnails.urls')),
)
