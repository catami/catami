"""URL Mappings for the webinterface application.
"""
__author__ = 'Ariell Friedman'

from django.conf.urls import patterns, url
#from django.contrib.auth.models import User


urlpatterns = patterns('webinterface.views',
    url(r'^$', 'index', name='index'),
    url(r'^explore$', 'explore'),
    #url(r'^viewcollection$', 'viewcollection'),
    url(r'^collections$', 'collections'),
    url(r'^collections/(?P<collection_id>\d+)/$', 'viewcollection'),
    url(r'^mycollections$', 'mycollections'),
    url(r'^mycollections_all$', 'mycollections_all'),
    url(r'^mycollections_recent$', 'mycollections_recent'),
    url(r'^publiccollections$', 'publiccollections'),
    url(r'^publiccollections_all$', 'publiccollections_all'),
    url(r'^publiccollections_recent$', 'publiccollections_recent'),
    url(r'^viewsubset$', 'viewsubset'),
    url(r'^allsubsets$', 'allsubsets'),
    url(r'^mysubsets$', 'mysubsets'),
    url(r'^publicsubsets$', 'publicsubsets'),
    url(r'^imageview$', 'imageview'),
    url(r'^imageannotate$', 'imageannotate'),
    url(r'^imageedit$', 'imageedit'),
)
