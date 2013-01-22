from django.conf.urls import patterns, include, url
from tastypie.api import Api
import collection.api

dev_api = Api(api_name='dev')
v1_api = Api(api_name='v1')

dev_api.register(collection.api.CollectionResource())

urlpatterns = patterns('',
    (r'', include(dev_api.urls)),
    (r'', include(v1_api.urls)),
)
