from tastypie import fields
from tastypie.resources import ModelResource
from .models import Collection

from tastypie.authentication import Authentication, SessionAuthentication, MultiAuthentication, ApiKeyAuthentication

from jsonapi.security import CollectionAuthorization
from jsonapi.api import UserResource


class CollectionResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    parent = fields.ForeignKey('collection.api.CollectionResource', 'parent', null=True)
    class Meta:
        queryset = Collection.objects.all()
        resource_name = "collection"
        authentication = MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication(), Authentication())
        authorization = CollectionAuthorization()
        detail_allowed_methods = ['get', 'delete', 'put']
        list_allowed_methods = ['get']
        filtering = {
            'is_public': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'parent': 'exact'
        }

    def dehydrate(self, bundle):
        """Add an image_count field to CollectionResource."""
        bundle.data['image_count'] = Collection.objects.get(pk=bundle.data['id']).images.count()
        return bundle
