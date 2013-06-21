from tastypie import fields
from tastypie.resources import ModelResource
from projects.models import (Project,
                             GenericAnnotationSet,
                             GenericPointAnnotation,
                             GenericWholeImageAnnotation,
                             AnnotationCodes,
                             QualifierCodes)
from catamidb.api import GenericImageResource
from tastypie.authentication import (Authentication,
                                     SessionAuthentication,
                                     MultiAuthentication,
                                     ApiKeyAuthentication)
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
    get_users_with_perms, get_groups_with_perms)
from jsonapi.api import UserResource
from jsonapi.security import get_real_user_object
from projects import authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
import logging

logger = logging.getLogger(__name__)


# ==============================
# Integration of Backbone and tastypie.
# Usage: extend this resource to make model compatibile with Backbonejs
# ==============================
class BackboneCompatibleResource(ModelResource):
    class Meta:
        always_return_data = True

    def alter_list_data_to_serialize(self, request, data):
        return data["objects"]


# Used to allow authent of anonymous users for GET requests
class AnonymousGetAuthentication(SessionAuthentication):
    def is_authenticated(self, request, **kwargs):
        # let anonymous users in for GET requests - Authorisation logic will
        # stop them from accessing things not allowed to access
        if request.user.is_anonymous() and request.method == "GET":
            return True

        return super(AnonymousGetAuthentication, self).is_authenticated(
            request, **kwargs)


class ProjectAuthorization(Authorization):
    """
    Implements authorization for projects.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible project."""
        user = get_real_user_object(bundle.request.user)
        user_objects = get_objects_for_user(user, [
            'projects.view_project'], object_list)

        return user_objects

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this project."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_project', bundle.obj):
            return True

        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no create lists.")

    def create_detail(self, object_list, bundle):
        #Allow creates for Authenticated users

        if bundle.request.user.is_authenticated():
            return True

        raise Unauthorized(
            "You need to log in to create projects.")

    def delete_list(self, object_list, bundle):
        """Currently do not permit deletion of any project list.
        """
        raise Unauthorized(
            "You do not have permission to delete these project.")

    def delete_detail(self, object_list, bundle):
        """
        Check the user has permission to delete.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to delete this object
        if user.has_perm('projects.delete_project', bundle.obj):
            return True

        raise Unauthorized(
            "You do not have permission to delete this project.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a project.
        """
        # the original can be found in object_list
        #original = object_list.get(id=bundle.obj.id)
        user = get_real_user_object(bundle.request.user)
        if user.has_perm('projects.change_project', bundle.obj):
            # the user has permission to edit
            return True
        else:
            raise Unauthorized(
                "You don't have permission to edit this project"
            )


class GenericAnnotationSetAuthorization(Authorization):
    """
    Implements authorization for the GenericAnnotationSet.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible GenericAnnotationSet."""
        user = get_real_user_object(bundle.request.user)
        user_objects = get_objects_for_user(user, [
            'projects.view_genericannotationset'], object_list)

        return user_objects

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this GenericAnnotationSet."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_genericannotationset', bundle.obj):
            return True

        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no create lists.")

    def create_detail(self, object_list, bundle):
        #Allow creates for Authenticated users
        if bundle.request.user.is_authenticated():
            return True

        raise Unauthorized(
            "You need to log in to create annotation sets.")

    def delete_list(self, object_list, bundle):
        """Currently do not permit deletion of any GenericAnnotationSet list.
        """
        raise Unauthorized(
            "You do not have permission to delete these project.")

    def delete_detail(self, object_list, bundle):
        """
        Check the user has permission to delete.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to delete this object
        if user.has_perm('projects.delete_genericannotationset', bundle.obj):
            return True

        raise Unauthorized(
            "You do not have permission to delete this project.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a project.
        """

        user = get_real_user_object(bundle.request.user)
        if user.has_perm('projects.change_genericannotationset', bundle.obj):
            # the user has permission to edit
            return True
        else:
            raise Unauthorized(
                "You don't have permission to edit this project"
            )


class GenericPointAnnotationAuthorization(Authorization):
    """
    Implements authorization for the GenericPointAnnotations.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible GenericPointAnnotations."""
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        annotation_set_objects = get_objects_for_user(user, [
            'projects.view_genericannotationset'])

        # get all annotation points for the above allowable annotation sets
        point_annotations = GenericPointAnnotation.objects.select_related("generic_annotation_set")
        point_annotation_ids = (point_annotations.filter(generic_annotation_set__in=annotation_set_objects).
                          values_list('id'))

        #now filter out the deployments we are not allowed to see
        return object_list.filter(id__in=point_annotation_ids)

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this GenericPointAnnotation."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_genericannotationset', bundle.obj.generic_annotation_set):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no create lists.")

    def create_detail(self, object_list, bundle):
        #authenticated people can create items
        if bundle.request.user.is_authenticated():
            return True

        raise Unauthorized(
            "You don't have permission to create annotations on this annotation set.")

    def delete_list(self, object_list, bundle):
        """Currently do not permit deletion of any GenericAnnotationSet list.
        """
        raise Unauthorized("You do not have permission to delete these annotation points.")

    def delete_detail(self, object_list, bundle):
        """
        Check the user has permission to delete.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        #if the user is not authenticated they can't do anything
        if not bundle.request.user.is_authenticated():
           raise Unauthorized()

        # check the user has permission to edit the contained annotation set
        if user.has_perm('projects.change_genericannotationset', bundle.obj.generic_annotation_set):
            return True

        raise Unauthorized(
            "You do not have permission to delete this annotation point.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a project.
        """

        user = get_real_user_object(bundle.request.user)

        #if the user is not authenticated they can't do anything
        if not bundle.request.user.is_authenticated():
           raise Unauthorized()

        # check the user has permission to edit the contained annotation set
        if user.has_perm('projects.change_genericannotationset', bundle.obj.generic_annotation_set):
            return True

        raise Unauthorized("You don't have permission to edit this annotation point.")


class ProjectResource(BackboneCompatibleResource):
    #owner = fields.ForeignKey(UserResource, 'owner', full=True)

    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = ProjectAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'name': 'exact',
            'owner': 'exact',
            'id': 'exact'
        }

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created Project. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        #create the bundle
        super(ProjectResource, self).obj_create(bundle)

        #make sure we apply permissions to this newly created object
        authorization.apply_project_permissions(user, bundle.obj)

        return bundle

    def dehydrate(self, bundle):
        """Add an image_count field to ProjectResource."""
        bundle.data['image_count'] = Project.objects.get(pk=bundle.data[
            'id']).generic_images.count()

        return bundle


class GenericAnnotationSetResource(BackboneCompatibleResource):
    project = fields.ForeignKey(ProjectResource, 'project', full=True)

    class Meta:
        queryset = GenericAnnotationSet.objects.all()
        resource_name = "generic_annotation_set"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = GenericAnnotationSetAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'project': 'exact',
            'name': 'exact',
            'owner': 'exact',
            'id': 'exact'
        }

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created GenericAnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        #create the bundle
        super(GenericAnnotationSetResource, self).obj_create(bundle)

        #make sure we apply permissions to this newly created object
        authorization.apply_generic_annotation_set_permissions(user, bundle.obj)

        return bundle


class GenericPointAnnotationResource(BackboneCompatibleResource):
    generic_annotation_set = fields.ForeignKey(GenericAnnotationSetResource, 'generic_annotation_set', full=True)
    image = fields.ForeignKey(GenericImageResource, 'image', full=True)

    class Meta:
        queryset = GenericPointAnnotation.objects.all()
        resource_name = "generic_point_annotation"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = GenericPointAnnotationAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'image': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'annotation_caab_code': 'exact',
            'qualifier_short_name': 'exact',
            'generic_annotation_set': 'exact',
        }

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created GenericAnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        super(GenericPointAnnotationResource, self).obj_create(bundle)

        # NOTE: we can't check permissions on related objects until the bundle
        # is created - django throws an exception. What we need to do here is
        # check permissions. If the user does not have permissions we delete
        # the create object.
        if not user.has_perm('projects.change_genericannotationset', bundle.obj.generic_annotation_set):
            bundle.obj.delete()

        return bundle


class GenericWholeImageAnnotationResource(BackboneCompatibleResource):
    generic_annotation_set = fields.ForeignKey(GenericAnnotationSet, 'generic_annotation_set', full=True)
    image = fields.ForeignKey(GenericImageResource, 'image', full=True)

    class Meta:
        queryset = GenericWholeImageAnnotation.objects.all()
        resource_name = "generic_whole_image_annotation"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = ProjectAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'image': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'annotation_caab_code': 'exact',
            'qualifier_short_name': 'exact',
            'generic_annotation_set': 'exact',
        }


class AnnotationCodesResource(BackboneCompatibleResource):
    parent = fields.ForeignKey('projects.api.AnnotationCodesResource', 'parent', null=True)

    class Meta:
        queryset = AnnotationCodes.objects.all()
        resource_name = "annotation_code"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        #authorization = ProjectAuthorization()
        detail_allowed_methods = ['get']
        list_allowed_methods = ['get']

        filtering = {
            'parent': ALL_WITH_RELATIONS,
            'code_name': ALL,
            'id': ALL,
        }


class QualifierCodesResource(BackboneCompatibleResource):
    parent = fields.ForeignKey('projects.api.QualifierCodesResource', 'parent', full=True)

    class Meta:
        queryset = QualifierCodes.objects.all()
        resource_name = "qualifier_code"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        #authorization = ProjectAuthorization()
        detail_allowed_methods = ['get']
        list_allowed_methods = ['get']
        filtering = {
            'short_name': 'exact',
            'id': 'exact',
            'parent': 'exact',
        }