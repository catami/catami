import traceback
from tastypie import fields
from tastypie.resources import ModelResource
from catamidb.models import GenericImage
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
    get_users_with_perms, get_groups_with_perms, get_perms)
from jsonapi.api import UserResource
from jsonapi.security import get_real_user_object
from projects import authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from datetime import datetime
from random import sample
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNotImplemented
import random
import logging

logger = logging.getLogger(__name__)


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

        print get_perms(user, bundle.obj)
        print bundle.obj.name
        print bundle.obj.owner

        if user.has_perm('projects.change_project', bundle.obj):
            # the user has permission to edit
            return True
        else:
            print "should not see this proj"
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
            "You do not have permission to delete these annotation sets.")

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
                "You don't have permission to edit this annotation set"
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


class ProjectResourceLite(ModelResource):
    """
    This is a light resource for use in lists. Packing all the images in the response
    slows things down.
    """
    owner = fields.ForeignKey(UserResource, 'owner', full=True)

    class Meta:
        always_return_data = True,
        queryset = Project.objects.all()
        resource_name = "project_lite"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = ProjectAuthorization()
        detail_allowed_methods = ['get']
        list_allowed_methods = ['get']
        filtering = {
            'name': ALL,
            'owner': ALL,
            'id': 'exact'
        }


class ProjectResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    generic_images = fields.ManyToManyField(GenericImageResource, 'generic_images', full=True)

    class Meta:
        always_return_data = True,
        queryset = Project.objects.all()
        resource_name = "project"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = ProjectAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'name': ALL,
            'owner': ALL,
            'generic_images': ALL_WITH_RELATIONS,
            'id': 'exact'
        }
        #excludes = ['owner', 'creation_date', 'modified_date']

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created Project. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        #put the created and modified dates on the object
        create_modified_date = datetime.now()
        bundle.data['creation_date'] = create_modified_date
        bundle.data['modified_date'] = create_modified_date

        #attach current user as the owner
        bundle.data['owner'] = user

        #create the bundle
        super(ProjectResource, self).obj_create(bundle)

        #make sure we apply permissions to this newly created object
        authorization.apply_project_permissions(user, bundle.obj)

        return bundle

    def dehydrate(self, bundle):
        # Add an image_count field to ProjectResource.
        bundle.data['image_count'] = Project.objects.get(pk=bundle.data[
            'id']).generic_images.count()

        # Add the map_extent of all the images in this project
        images = Project.objects.get(id=bundle.obj.id).generic_images.all()
        images = GenericImage.objects.filter(id__in=images)
        map_extent = ""
        if len(images) != 0:
            map_extent = images.extent().__str__()

        bundle.data['map_extent'] = map_extent

        return bundle


class GenericAnnotationSetResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    generic_images = fields.ManyToManyField(GenericImageResource, 'generic_images', full=True, blank=True, null=True)

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

    def random_sample_images(self, project, sample_size):
        """ Randomly sample images from the parent project and
            attach them to this annotation set. """

        project_images = project.generic_images.all()
        sampled_images = sample(project_images, int(sample_size))

        return sampled_images

    def stratified_sample_images(self, project, sample_size):
        """ Stratified sample images from the parent project and
            attach them to this resource. """

        project_images = project.generic_images.all()
        every_nth = project_images.count()/int(sample_size)

        sampled_images = project_images[0:project_images.count():every_nth]

        return sampled_images

    def apply_random_sampled_points(self, annotation_set, sample_size):
        """ Randomly apply points to the images attached to this annotation
            set """

        images = annotation_set.generic_images.all()

        # iterate through the images and create points
        for image in images:
            for i in range(int(sample_size)):
                x = random.random()
                y = random.random()

                point_annotation = GenericPointAnnotation()

                point_annotation.generic_annotation_set = annotation_set
                point_annotation.image = image
                point_annotation.owner = annotation_set.owner
                point_annotation.x = x
                point_annotation.y = y

                point_annotation.annotation_caab_code = "00000000" # not considered
                point_annotation.qualifier_short_name = "" # not considered

                point_annotation.save()

    def apply_stratified_sampled_points(self, annotation_set, sample_size):
        """ Apply points to the images attached to this annotation set using
            stratified sampling """

        #TODO: implement
        return None

    def do_sampling_operations(self, bundle):
        """ Helper function to hold all the sampling logic """

        # subsample and set the images
        image_sample_size = bundle.data['image_sample_size']
        image_sampling_methodology = bundle.data['image_sampling_methodology']

        if image_sampling_methodology == '0':
            bundle.obj.generic_images = self.random_sample_images(bundle.obj.project, image_sample_size)
        elif image_sampling_methodology == '1':
            bundle.obj.generic_images = self.stratified_sample_images(bundle.obj.project, image_sample_size)
        else:
            raise Exception("Image sampling method not implemented.")

        #save the object with the new images on it
        bundle.obj.save()

        # subsample points based on methodologies
        point_sample_size = bundle.data['point_sample_size']
        annotation_methodology = bundle.data['annotation_methodology']

        if annotation_methodology == '0':
            self.apply_random_sampled_points(bundle.obj, point_sample_size)
        else:
            raise Exception("Point sampling method not implemented.")

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created GenericAnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object.
        """
        # get real user
        user = get_real_user_object(bundle.request.user)

        #put the created and modified dates on the object
        create_modified_date = datetime.now()
        bundle.data['creation_date'] = create_modified_date
        bundle.data['modified_date'] = create_modified_date

        bundle.data['generic_images'] = ''

        #attach current user as the owner
        bundle.data['owner'] = user

        #create the bundle
        super(GenericAnnotationSetResource, self).obj_create(bundle)

        #generate image subsamples and points
        try:
            self.do_sampling_operations(bundle)
        except Exception:
            #delete the object that was created
            bundle.obj.delete()

            #return not implemented response
            raise ImmediateHttpResponse(HttpNotImplemented("Unable to create annotation set."))

        #make sure we apply permissions to this newly created object
        authorization.apply_generic_annotation_set_permissions(user, bundle.obj)

        return bundle


class GenericPointAnnotationResource(ModelResource):
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


class GenericWholeImageAnnotationResource(ModelResource):
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


class AnnotationCodesResource(ModelResource):
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


class QualifierCodesResource(ModelResource):
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