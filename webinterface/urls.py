"""URL Mappings for the webinterface application.
"""
from catamidb import authorization
from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.views.generic.simple import direct_to_template

dajaxice_autodiscover()


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
    url(r'^staging/', include('staging.urls')),

    # Projects
    #url(r'^projects$', 'projects'),
    url(r'^projects/$', 'projects'),
    url(r'^projects/(?P<project_id>\d+)/$', 'project_view'),
    url(r'^projects/(?P<project_id>\d+)/configure/$', 'project_configure'),
    url(r'^projects/(?P<project_id>\d+)/configure/(?P<annotation_set_id>\d+)/$', 'project_annotate'),

    #Collection detail Views
    #url(r'^collections/(?P<collection_id>\d+)/$', 'view_collection'),
#    url(
#        r'^collections/(?P<collection_id>\d+)/workset/(?P<workset_id>\d+)/$',
#        'view_workset'),
    #url(r'^my_collections$', 'my_collections'),
    #url(r'^my_collections_all$', 'my_collections_all'),
    #url(r'^my_collections_recent$', 'my_collections_recent'),
    #url(r'^public_collections$', 'public_collections'),
    #url(r'^public_collections_all$', 'public_collections_all'),
    #url(r'^public_collections_recent$', 'public_collections_recent'),

    #Collection Object Views
    url(r'^view_subset$', 'view_subset'),
    url(r'^all_subsets/(?P<collection_id>\d+)/$',
        'all_subsets'),
    url(r'^my_subsets$', 'my_subsets'),
    url(r'^public_subsets$', 'public_subsets'),
    url(r'^imageview$', 'image_view'),
#    url(r'^imageannotate$', 'image_annotate'),
    url(r'^imageannotate/(?P<image_id>\d+)/$', 'image_annotate'),
    url(r'^inlineimageannotate/(?P<image_id>\d+)/$', 'inline_image_annotate'),

    url(r'^imageedit$', 'image_edit'),

    #Collection Management
    #url(r'^collections/create/$',
    #    'create_collection_from_deployments'),
    #url(r'^collections/create/$', 'create_collection_from_explore'),
    #url(r'^collections/getcollectionextent$', 'get_collection_extent'),

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
    url(r'^report/', include('dbadmintool.urls')),

    # userena
    (r'^accounts/', include('accounts.urls')),
    url(r'^logout/$', 'logout_view'),

    # Dajaxice
    #url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    url(r'^explore$', 'explore'),
    url(r'^explore/getmapextent$',
        'get_multiple_deployment_extent'),

    url(r'^explore_campaign/(?P<campaign_id>\d+)/$',
        'explore_campaign'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

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
    url(r'^thumbnails/', include('restthumbnails.urls')),
)
