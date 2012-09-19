__author__ = 'lachlan'

from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
    url(r'^$', 'staging.views.index'),
    url(r'^auv/import$', 'staging.views.auvimport'),
    url(r'^auv/imported$', 'staging.views.auvimported'),
)

