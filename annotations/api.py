from tastypie import fields
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, SessionAuthentication, MultiAuthentication, ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound, BadRequest, Unauthorized

import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms)

from collection.models import Collection

from . import models 

import logging

logger = logging.getLogger(__name__)

class AnnotationCodeResource(ModelResource):
    parent = fields.ForeignKey('annotations.api.AnnotationCodeResource', 'parent')
    
    class Meta:
        queryset = models.AnnotationCode.objects.all()
        resource_name = "annotation_code"
        # use defaults - no special permissions are needed here
        # for authorization and authentication
        filtering = {
            'parent': ALL_WITH_RELATIONS,
            'code_name': ALL,
        }
        allowed_methods = ['get']
    

class QualifierCodeResource(ModelResource):
    
    class Meta:
        queryset = models.QualifierCode.objects.all()
        resource_name = "qualifier_code"
        # use defaults - no special permissions are needed here
        # for authorization and authentication
        filtering = {
            'modifier_name': ALL,
        }
        allowed_methods = ['get']


class PointAnnotationSetResource(ModelResource):
    collection = fields.ForeignKey('collection.api.CollectionResource', 'collection')
    
    class Meta:
        queryset = models.PointAnnotationSet.objects.all()
        resource_name = "point_annotation_set"
        filtering = {
            'collection': ALL_WITH_RELATIONS,
            'name': ALL,
        }


class PointAnnotationResource(ModelResource):
    image = fields.ForeignKey('catamidb.Image', 'image')
    label = fields.ForeignKey(AnnotationCodeResource, 'label')
    qualifier = fields.ForeignKey(QualifierCodeResource, 'qualifier')
    #labeller = fields.ForeignKey( # User
    annotation_set = fields.ForeignKey(PointAnnotationSetResource, 'set')

    class Meta:
        queryset = models.PointAnnotation.objects.all()
        resource_name = "point_annotation"
        filtering = {
            'image': ALL_WITH_RELATIONS,
            'label': ALL_WITH_RELATIONS,
            'qualifier': ALL_WITH_RELATIONS,
            'annotation_set': ALL_WITH_RELATIONS,
            'level': ALL,
        }
        allowed_methods = ['get']


