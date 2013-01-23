from tastypie import fields
from tastypie.resources import ModelResource
from .models import Collection

from tastypie.authentication import BasicAuthentication

from jsonapi.security import CollectionAuthorization


class CollectionResource(ModelResource):
    class Meta:
        queryset = Collection.objects.all()
        resource_name = "collection"
        authentication = BasicAuthentication()
        authorization = CollectionAuthorization()
