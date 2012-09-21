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
    url(r'^campaigns/(?P<campaign_id>\d+)/$', 'Force.views.campaignDetail'),
    url(r'^auvdeployments/(?P<auvdeployment_id>\d+)/$', 'Force.views.auvdeploymentDetail'),

    #url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
)
