import traceback
import csv
import StringIO
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.utils import simplejson
from tastypie import fields
# import tastypie
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from catamidb.models import Image, ImageManager
from projects.models import (Project,
                             AnnotationSet,
                             PointAnnotation,
                             WholeImageAnnotation,
                             AnnotationCodes,
                             QualifierCodes, PointAnnotationManager)
from catamidb.api import ImageResource
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
# from random import sample
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNotImplemented, HttpBadRequest, HttpGone, HttpMultipleChoices
# import random
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
        user_objects = get_objects_for_user(user, ['projects.view_project'], object_list)

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

        raise Unauthorized("You do not have permission to delete this project.")

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
            raise Unauthorized("You don't have permission to edit this project")


class AnnotationSetAuthorization(Authorization):
    """
    Implements authorization for the AnnotationSet.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible AnnotationSet."""
        user = get_real_user_object(bundle.request.user)
        user_objects = get_objects_for_user(user, ['projects.view_annotationset'], object_list)

        return user_objects

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this AnnotationSet."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_annotationset', bundle.obj):
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
        """Currently do not permit deletion of any AnnotationSet list.
        """
        raise Unauthorized("You do not have permission to delete these annotation sets.")

    def delete_detail(self, object_list, bundle):
        """
        Check the user has permission to delete.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to delete this object
        if user.has_perm('projects.delete_annotationset', bundle.obj):
            return True

        raise Unauthorized("You do not have permission to delete this project.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a project.
        """

        user = get_real_user_object(bundle.request.user)
        if user.has_perm('projects.change_annotationset', bundle.obj):
            # the user has permission to edit
            return True
        else:
            raise Unauthorized("You don't have permission to edit this annotation set")


class PointAnnotationAuthorization(Authorization):
    """
    Implements authorization for the PointAnnotations.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible PointAnnotations."""

        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        annotation_set_objects = get_objects_for_user(user, ['projects.view_annotationset'])

        # get all annotation points for the above allowable annotation sets
        point_annotations = PointAnnotation.objects.select_related("annotation_set")
        point_annotation_ids = (point_annotations.filter(annotation_set__in=annotation_set_objects).values_list('id'))

        #now filter out the deployments we are not allowed to see
        return object_list.filter(id__in=point_annotation_ids)

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this PointAnnotation."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_annotationset', bundle.obj.annotation_set):
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
        """Currently do not permit deletion of any AnnotationSet list.
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
        if user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
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
        if user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            return True

        raise Unauthorized("You don't have permission to edit this annotation point.")


class WholeImageAnnotationAuthorization(Authorization):
    """
    Implements authorization for WholeImageAnnotations.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible WholeImageAnnotation."""

        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        annotation_set_objects = get_objects_for_user(user, ['projects.view_annotationset'])

        # get all whole image annotation points for the above allowable annotation sets
        whole_image_annotations = WholeImageAnnotation.objects.select_related("annotation_set")
        whole_image_annotation_ids = (whole_image_annotations.filter(annotation_set__in=annotation_set_objects).values_list('id'))

        #now filter out the deployments we are not allowed to see
        return object_list.filter(id__in=whole_image_annotation_ids)

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this PointAnnotation."""

        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('projects.view_annotationset', bundle.obj.annotation_set):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no create lists.")

    def create_detail(self, object_list, bundle):

        #authenticated people can create items
        if bundle.request.user.is_authenticated():
            return True

        raise Unauthorized("You don't have permission to create whole image annotations on this annotation set.")

    def delete_list(self, object_list, bundle):
        """Currently do not permit deletion of any AnnotationSet list.
        """
        raise Unauthorized("You do not have permission to delete these whole image annotation points.")

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
        if user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            return True

        raise Unauthorized("You do not have permission to delete this annotation point.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a project.
        """

        user = get_real_user_object(bundle.request.user)

        #if the user is not authenticated they can't do anything
        if not bundle.request.user.is_authenticated():
            raise Unauthorized()

        # check the user has permission to edit the contained annotation set
        if user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            return True

        raise Unauthorized("You don't have permission to edit this whole image annotation.")


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


class ModelResource(ModelResource):
    def prepend_urls(self):
        urls = []

        for name, field in self.fields.items():
            if isinstance(field, fields.ToManyField):
                resource = r"^(?P<resource_name>{resource_name})/(?P<{related_name}>.+)/{related_resource}/$".format(
                    resource_name=self._meta.resource_name,
                    related_name=field.related_name,
                    related_resource=field.attribute,
                    )
                resource = url(resource, field.to_class().wrap_view('get_list'), name="api_dispatch_detail")
                urls.append(resource)
        return urls


class ProjectResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    images = fields.ManyToManyField(ImageResource, 'images', blank=True)

    class Meta:
        always_return_data = True,
        queryset = Project.objects.all()
        resource_name = "project"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = ProjectAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        filtering = {
            'name': ALL,
            'owner': ALL,
            'images': ALL_WITH_RELATIONS,
            'id': 'exact'
        }
        #excludes = ['owner', 'creation_date', 'modified_date']

    def prepend_urls(self):
        return [
            url(r"^(?P<project>%s)/create_project%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('create_project'), name="create_project"),
            url(r"^(?P<project>%s)/(?P<pk>\w[\w/-]*)/csv%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_csv'), name="api_get_csv"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/images%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_images'), name="api_get_images"),            
        ]

    def get_images(self, request, **kwargs):
        """
        This is a nested function so that we can do paginated thumbnail queries on the image resource
        """

        # need to create a bundle for tastypie
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI.")

        # get all the images related to this project
        project_images = Project.objects.get(id=obj.pk).images.all()

        # create the id string list to send to the next API call
        # TODO: this is not ideal, best find a better way to deal with this
        image_ids = ""
        for image in project_images:
            image_ids += image.id.__str__() + ","

        # strip the comma from the end
        image_ids = image_ids[:-1]

        # call the image resource to give us what we want
        image_resource = ImageResource()
        return image_resource.get_list(request, id__in=image_ids)

    def get_csv(self, request, **kwargs):
        """
        Special handler function to export project as CSV
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + kwargs['project'] + '.csv"'
                

        # get all the images related to this project
        images = Project.objects.get(id=kwargs['pk']).images.all()       

        #get all annotation sets related to this project
        sets = AnnotationSet.objects.filter(project=kwargs['pk'])

        writer = csv.writer(response)
        writer.writerow(['Image Name', 'Campaign Name', 'Deployment Name', 
                         'Image Location', 'Point in Image', 'Annotation Code', 'Annotation Name'])        
        
        for set in sets:
            for image in set.images.all():
                point_bundle = Bundle()
                point_bundle.request = request
                point_bundle.data = dict(image=image.id, annotation_set=set.id)
                points = PointAnnotationResource().obj_get_list(point_bundle, image=image.id)
                for point in points: 
                    code_name = ''
                    if point.annotation_caab_code and point.annotation_caab_code is not u'':
                        code = AnnotationCodes.objects.filter(caab_code=point.annotation_caab_code)                    
                        if code and code is not None and len(code) > 0:
                            code_name = code[0].code_name
                    writer.writerow([image.image_name, image.deployment.campaign.short_name, 
                                     image.deployment.short_name, image.position, 
                                     (str(point.x) + ' , ' + str(point.y)), 
                                     point.annotation_caab_code, code_name])

        return response

    def create_project(self, request, **kwargs):
        """
        Special handler function to create a project based on search criteria from images
        """
        json_data = simplejson.loads(request.body)

        #pull the query parameters out
        name = json_data['name']
        description = json_data['description']
        deployment_id = json_data['deployment_id']
        image_sampling_methodology = json_data['image_sampling_methodology']
        image_sample_size = json_data['image_sample_size']
        annotation_methodology = json_data['annotation_methodology']
        point_sample_size = json_data['point_sample_size']
        annotation_type = json_data['annotation_type']

        #only proceed with all parameters
        if (name and description and deployment_id and image_sampling_methodology and
            image_sample_size and annotation_methodology and point_sample_size) is not None:

            #get the images we are interested in
            image_bundle = Bundle()
            image_bundle.request = request
            image_bundle.data = dict(deployment=deployment_id)
            images = ImageResource().obj_get_list(image_bundle, deployment=deployment_id)

            #check the the sample size is not larger than the number of images in our image list
            if int(image_sample_size) > len(images):
                return HttpResponse(content="{\"error_message\": \"Your image sample size is larger than the number of images in the Deployment. Pick a smaller number.\"}",
                                    status=400,
                                    content_type='application/json')

            # subsample and set the images
            if image_sampling_methodology == '0':
                image_subset = ImageManager().random_sample_images(images, image_sample_size)
            elif image_sampling_methodology == '1':
                image_subset = ImageManager().stratified_sample_images(images, image_sample_size)
            else:
                raise Exception("Image sampling method not implemented.")

            #create the project
            project_bundle = Bundle()
            project_bundle.request = request
            project_bundle.data = dict(name=name, description=description, images=images)
            new_project = self.obj_create(project_bundle)

            #create the annotation set for the project
            annotation_set_bundle = Bundle()
            annotation_set_bundle.request = request
            annotation_set_bundle.data = dict(project=new_project, name="", description="",
                                              image_sampling_methodology=image_sampling_methodology,
                                              image_sample_size=image_sample_size,
                                              annotation_methodology=annotation_methodology,
                                              point_sample_size=point_sample_size, 
                                              images=image_subset,
                                              annotation_type=annotation_type)
            
            AnnotationSetResource().obj_create(annotation_set_bundle)

            # build up a response with a 'Location', so the client knows the project id which is created
            kwargs = dict (resource_name=self._meta.resource_name,
                            pk=new_project.obj.id,
                            api_name=self._meta.api_name)

            response = HttpResponse(content_type='application/json')
            response['Location'] = self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)
            return response

        return self.create_response(request, "Not all fields were provided.", response_class=HttpBadRequest())

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
            'id']).images.count()

        # Add the map_extent of all the images in this project
        images = Project.objects.get(id=bundle.obj.id).images.all()
        images = Image.objects.filter(id__in=images)
        map_extent = ""
        if len(images) != 0:
            map_extent = images.extent().__str__()

        bundle.data['map_extent'] = map_extent

        return bundle


class AnnotationSetResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    images = fields.ManyToManyField(ImageResource, 'images', full=True, blank=True, null=True)

    class Meta:
        queryset = AnnotationSet.objects.all()
        resource_name = "annotation_set"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = AnnotationSetAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'project': 'exact',
            'name': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'annotation_type' : 'exact'
        }

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/images%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_images'), name="api_get_images"),
        ]

    def get_images(self, request, **kwargs):
        """
        This is a nested function so that we can do paginated thumbnail queries on the image resource
        """

        # need to create a bundle for tastypie
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI.")

        # get all the images related to this project
        annotation_set_images = AnnotationSet.objects.get(id=obj.pk).images.all()

        # create the id string list to send to the next API call
        # TODO: this is not ideal, best find a better way to deal with this
        image_ids = ""
        for image in annotation_set_images:
            image_ids += image.id.__str__() + ","

        # strip the comma from the end
        image_ids = image_ids[:-1]

        # call the image resource to give us what we want
        image_resource = ImageResource()
        return image_resource.get_list(request, id__in=image_ids)

    def do_sampling_operations(self, bundle):
        """ Helper function to hold all the sampling logic """

        # subsample points based on methodologies
        #bundle.obj.images = bundle.data['image_subset']
        point_sample_size = bundle.data['point_sample_size']
        annotation_methodology = bundle.data['annotation_methodology']
        
        if annotation_methodology == '0':
            PointAnnotationManager().apply_random_sampled_points(bundle.obj, point_sample_size)
        else:
            raise Exception("Point sampling method not implemented.")

    def obj_create(self, bundle, **kwargs):
        """
        We are overriding this function so we can get access to the newly
        created AnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object.
        """
        # get real user
        user = get_real_user_object(bundle.request.user)

        #put the created and modified dates on the object
        create_modified_date = datetime.now()
        bundle.data['creation_date'] = create_modified_date
        bundle.data['modified_date'] = create_modified_date

        #bundle.data['images'] = ''

        #attach current user as the owner
        bundle.data['owner'] = user

        #create the bundle
        super(AnnotationSetResource, self).obj_create(bundle)
        #generate image subsamples and points
        try:
            self.do_sampling_operations(bundle)
        except Exception:
            #delete the object that was created
            bundle.obj.delete()

            #return not implemented response
            raise ImmediateHttpResponse(HttpNotImplemented("Unable to create annotation set."))

        #make sure we apply permissions to this newly created object
        authorization.apply_annotation_set_permissions(user, bundle.obj)
                
        return bundle


class PointAnnotationResource(ModelResource):
    annotation_set = fields.ForeignKey(AnnotationSetResource, 'annotation_set')
    image = fields.ForeignKey(ImageResource, 'image')

    class Meta:
        queryset = PointAnnotation.objects.all()
        resource_name = "point_annotation"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = PointAnnotationAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        filtering = {
            'image': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'annotation_caab_code': 'exact',
            'qualifier_short_name': 'exact',
            'annotation_set': 'exact',
        }

    def obj_create(self, bundle, **kwargs):
        """
        We are overriding this function so we can get access to the newly
        created AnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        super(PointAnnotationResource, self).obj_create(bundle)

        # NOTE: we can't check permissions on related objects until the bundle
        # is created - django throws an exception. What we need to do here is
        # check permissions. If the user does not have permissions we delete
        # the create object.
        if not user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            bundle.obj.delete()

        return bundle


class WholeImageAnnotationResource(ModelResource):
    annotation_set = fields.ForeignKey(AnnotationSetResource, 'annotation_set')
    image = fields.ForeignKey(ImageResource, 'image')

    class Meta:
        queryset = WholeImageAnnotation.objects.all()
        resource_name = "whole_image_annotation"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = WholeImageAnnotationAuthorization()
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'image': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'annotation_caab_code': 'exact',
            'qualifier_short_name': 'exact',
            'annotation_set': 'exact',
        }

    def obj_create(self, bundle, **kwargs):
        """
        We are overriding this function so we can get access to the newly
        created AnnotationSet. Once we have reference to it, we can apply
        object level permissions to the object. Copied from PointAnnotationResource
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        super(WholeImageAnnotationResource, self).obj_create(bundle)

        # NOTE: we can't check permissions on related objects until the bundle
        # is created - django throws an exception. What we need to do here is
        # check permissions. If the user does not have permissions we delete
        # the create object.
        if not user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            bundle.obj.delete()

        return bundle


class AnnotationCodesResource(ModelResource):
    parent = fields.ForeignKey('projects.api.AnnotationCodesResource', 'parent', null=True)

    class Meta:
        queryset = AnnotationCodes.objects.all()
        resource_name = "annotation_code"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
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
        detail_allowed_methods = ['get']
        list_allowed_methods = ['get']
        filtering = {
            'short_name': 'exact',
            'id': 'exact',
            'parent': 'exact',
        }
