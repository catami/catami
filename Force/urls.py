__author__ = 'ivec'

from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from Force.models import Campaign

urlpatterns = patterns('',
    url(r'^$', 'Force.views.index'),
    #url(r'^campaigns/',
    #    ListView.as_view(
    #        queryset=Campaign.objects.all(),
    #        context_object_name='campaignList',
    #        template_name='Force/CampaignList.html')),

    url(r'^addCampaign', 'Force.views.add_campaign'),
    url(r'^auvdeployments/$', 'Force.views.auvdeployments'),
    url(r'^campaigns/$', 'Force.views.campaigns'),
    url(r'^campaigns/(?P<campaign_id>\d+)/$', 'Force.views.campaign_detail'),
    url(r'^auvdeployments/(?P<auvdeployment_id>\d+)/$', 'Force.views.auvdeployment_detail'),

    #url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
)

from django.contrib.auth.views import login, logout

urlpatterns += patterns('',
    # existing patterns here...
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout)
)

