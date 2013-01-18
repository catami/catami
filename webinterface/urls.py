"""URL Mappings for the webinterface application.
"""
__author__ = 'Ariell Friedman'

from django.conf.urls import patterns, url
#from django.contrib.auth.models import User


urlpatterns = patterns('webinterface.views',
    url(r'^$', 'index', name='index'),
    url(r'^explore$', 'explore'),
    url(r'^viewcollection$', 'viewcollection'),
    url(r'^allcollections$', 'allcollections'),
    url(r'^mycollections$', 'mycollections'),
    url(r'^publiccollections$', 'publiccollections'),
    url(r'^viewsubset$', 'viewsubset'),
    url(r'^allsubsets$', 'allsubsets'),
    url(r'^mysubsets$', 'mysubsets'),
    url(r'^publicsubsets$', 'publicsubsets'),
    url(r'^imageview$', 'imageview'),
    url(r'^imageannotate$', 'imageannotate'),
    url(r'^imageedit$', 'imageedit'),
)
