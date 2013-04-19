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
from catamidb.models import Image

from . import models 
from catamidb.api import AnonymousGetAuthentication, get_real_user_object

import logging

logger = logging.getLogger(__name__)

class AnnotationCodeResource(ModelResource):
    parent = fields.ForeignKey('annotations.api.AnnotationCodeResource', 'parent', null=True)
    
    class Meta:
        queryset = models.AnnotationCode.objects.all()
        resource_name = "annotation_code"
        # use defaults - no special permissions are needed here
        # for authorization and authentication
        filtering = {
            'parent': ALL_WITH_RELATIONS,
            'code_name': ALL,
            'id': ALL,
        }
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        """Add a parent_id field to AnnotationCodeResource."""
        if bundle.obj.parent:
            bundle.data['parent_id'] = bundle.obj.parent.pk
        else:
            bundle.data['parent_id'] = None
        return bundle
    

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

class PointAnnotationSetAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        user_objects = get_objects_for_user(
                user,
                ['annotations.view_pointannotationset'],
                object_list
            )

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        ### DEBUG
        print bundle.obj

        # check the user has permission to view this object
        if user.has_perm('annotations.view_pointannotationset', bundle.obj):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check if they are allowed to create point annotation sets
        if user.has_perm('catamidb.create_pointannotationset', bundle.obj):
            return True

        raise Unauthorized("You are not allowed to create point sets.")

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

class PointAnnotationSetResource(ModelResource):
    collection = fields.ForeignKey('collection.api.CollectionResource', 'collection')
    
    class Meta:
        queryset = models.PointAnnotationSet.objects.all()
        resource_name = "point_annotation_set"
        filtering = {
            'collection': ALL_WITH_RELATIONS,
            'name': ALL,
        }
        allowed_methods = ['get', 'post']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                ApiKeyAuthentication())
        authorization = PointAnnotationSetAuthorization()


class PointAnnotationAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        # may be able to cache the lookup based on if have seen that
        # annotationset before
        user_objects = []
        for o in object_list:
            if user.has_perm('annotations.viewpointannotationset', o.annotation_set):
                user_objects.append(o)

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('annotations.view_pointannotation', bundle.obj):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        # get real user
        raise Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class PointAnnotationResource(ModelResource):
    image = fields.ForeignKey('catamidb.api.ImageResource', 'image')
    label = fields.ForeignKey(AnnotationCodeResource, 'label')
    qualifiers = fields.ToManyField(QualifierCodeResource, 'qualifiers')
    #labeller = fields.ForeignKey( # User
    annotation_set = fields.ForeignKey(PointAnnotationSetResource, 'annotation_set')

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
        allowed_methods = ['get', 'patch']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                ApiKeyAuthentication())
        authorization = PointAnnotationAuthorization()

    def obj_get_list(self, bundle, **kwargs):
        """Overrides the given method from ModelResource.

        This is to enable creation of the annotation points on
        first retrieval.

        Must have filter for image & annotation set. And nothing else.
        """

        filters = {}
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()

        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        # check if we match the exact filters required...
        # if extras, or either missing/repeated then ignore
        # and act as normal
        extras = False
        image_restriction = False
        set_restriction = False

        image_id = 0
        set_id = 0
        # check that the only two restrictions are this...
        for k, v in applicable_filters.iteritems():
            if not set_restriction and k == 'annotation_set__exact':
                set_restriction = True
                set_id = v
            elif not image_restriction and k == 'image__exact':
                image_restriction = True
                image_id = v
            else:
                extras = True

        if image_restriction and set_restriction and not extras:
            # get the set we are working with
            annotation_set = models.PointAnnotationSet.objects.get(id=set_id)

            # check if image in collection that annotationset links to
            image_in_collection = annotation_set.collection.images.filter(
                    id=image_id
                ).exists()

            # we want to ignore creating annotations for images not in the set
            if image_in_collection:
                # now check to see how many things there be
                # if count != n, then make them!
                # or do other error things if n != 0

                objects = self.apply_filters(bundle.request, applicable_filters)

                # if there are none then create them all
                # potentially should check for cases where count != expected
                if objects.count() == 0:
                    # create them all!
                    image = Image.objects.get(id=image_id)
                    user = get_real_user_object(bundle.request.user)
                    models.PointAnnotation.objects.create_annotations(
                            annotation_set,
                            image,
                            user
                        )

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)

            # prob at this point do it...

            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type.")


