"""@brief Django URLs for Catami data.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'Force.views.index'),
    #url(r'^campaigns/',
    #    ListView.as_view(
    #        queryset=Campaign.objects.all(),
    #        context_object_name='campaignList',
    #        template_name='Force/CampaignList.html')),

    url(r'^auvdeployments/$', 'Force.views.auvdeployments'),
    url(r'^auvdeployments/map/$', 'Force.views.auvdeployments_map'),
    url(r'^auvdeployments/(?P<auvdeployment_id>\d+)/$', 'Force.views.auvdeployment_detail'),
    url(r'^auvdeployments/(?P<auvdeployment_id>\d+)/images/$', 'Force.views.auvimage_list'),
    url(r'^auvdeployments/(?P<auvdeployment_id>\d+)/annotationview/(?P<image_index>\d+)/$', 'Force.views.annotationview'),

    url(r'^bruvdeployments/$', 'Force.views.bruvdeployments'),
    url(r'^bruvdeployments/map/$', 'Force.views.bruvdeployments_map'),
    url(r'^bruvdeployments/(?P<bruvdeployment_id>\d+)/$', 'Force.views.bruvdeployment_detail'),

    url(r'^dovdeployments/$', 'Force.views.dovdeployments'),
    url(r'^dovdeployments/(?P<dovdeployment_id>\d+)/$', 'Force.views.dovdeployment_detail'),

    url(r'^tvdeployments/$', 'Force.views.tvdeployments'),
    url(r'^tvdeployments/(?P<tvdeployment_id>\d+)/$', 'Force.views.tvdeployment_detail'),

    url(r'^tideployments/$', 'Force.views.tideployments'),
    url(r'^tideployments/(?P<tideployment_id>\d+)/$', 'Force.views.tideployment_detail'),

    url(r'^deployments/$', 'Force.views.deployments'),
    url(r'^deployments/map/$', 'Force.views.deployments_map'),

    url(r'^campaigns/$', 'Force.views.campaigns'),
    url(r'^campaigns/(?P<campaign_id>\d+)/$', 'Force.views.campaign_detail'),

    url(r'^spatialsearch/$', 'Force.views.spatialsearch'),

    #url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
)

from django.contrib.auth.views import login, logout

urlpatterns += patterns('',
    # existing patterns here...
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout)
)
