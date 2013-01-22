from tastypie import fields
from tastypie.resources import ModelResource
from .models import Collection

class CollectionResource(ModelResource):
    class Meta:
        queryset = Collection.objects.all()
        resource_name = "collection"
