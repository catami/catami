__author__ = 'ivec'

from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from Force.models import Campaign

urlpatterns = patterns('',
    url(r'^$', 'Force.views.index'),
    url(r'^campaigns/',
        ListView.as_view(
            queryset=Campaign.objects.all(),
            context_object_name='campaignList',
            template_name='Force/CampaignList.html')),
    url(r'^addCampaign', 'Force.views.add_campaign'),

    #url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
)
