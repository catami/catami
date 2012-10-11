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

    url(r'^deployments/$', 'Force.views.deployments'),
    url(r'^deployments/map/$', 'Force.views.deployments_map'),

    url(r'^addCampaign/$', 'Force.views.add_campaign'),
    url(r'^campaigns/$', 'Force.views.campaigns'),
    url(r'^campaigns/(?P<campaign_id>\d+)/$', 'Force.views.campaign_detail'),

    #url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
)

from django.contrib.auth.views import login, logout

urlpatterns += patterns('',
    # existing patterns here...
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout)
)