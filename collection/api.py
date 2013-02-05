from tastypie import fields
from tastypie.resources import ModelResource
from .models import Collection

from tastypie.authentication import BasicAuthentication

from jsonapi.security import CollectionAuthorization
from jsonapi.api import UserResource


class CollectionResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner')
    parent = fields.ForeignKey('collection.api.CollectionResource', 'parent', null=True)
    class Meta:
        queryset = Collection.objects.all()
        resource_name = "collection"
        authentication = BasicAuthentication()
        authorization = CollectionAuthorization()
        filtering = {
            'is_public': 'exact',
            'owner': 'exact'
        }
