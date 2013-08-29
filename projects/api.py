import traceback
import csv
import StringIO
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.utils import simplejson
import requests
from tastypie import fields
# import tastypie
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from catamiPortal import settings
from catamidb.models import Image, ImageManager
from projects.models import (Project,
                             AnnotationSet,
                             PointAnnotation,
                             WholeImageAnnotation,
                             AnnotationCodes,
                             QualifierCodes, 
                             PointAnnotationManager,
                             WholeImageAnnotationManager)
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

    def dehydrate(self, bundle):
        bundle.data['permissions'] = get_perms(get_real_user_object(bundle.request.user), bundle.obj)
        return bundle

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

        project = Project.objects.get(id=kwargs['pk'])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + project.name + '.csv"'
                

        # get all the images related to this project
        images = project.images.all()       

        #get all annotation sets related to this project
        sets = AnnotationSet.objects.filter(project=kwargs['pk'])

        writer = csv.writer(response)
        writer.writerow(['Annotation Set Type', 'Image Name', 'Campaign Name', 'Deployment Name', 
                         'Image Location', 'Point in Image', 'Annotation Code', 'Annotation Name'])        
        
        for set in sets:
            # 0 - Point, 1 - Whole Image    
            annotation_set_type = set.annotation_set_type
            for image in set.images.all():
                bundle = Bundle()
                bundle.request = request
                bundle.data = dict(image=image.id, annotation_set=set.id)
                if annotation_set_type == 0:
                    point_set = PointAnnotationResource().obj_get_list(bundle, image=image.id)
                    for point in point_set: 
                        code_name = ''
                        if point.annotation_caab_code and point.annotation_caab_code is not u'':
                            code = AnnotationCodes.objects.filter(caab_code=point.annotation_caab_code)
                            if code and code is not None and len(code) > 0:
                                code_name = code[0].code_name
                        writer.writerow(['Point', image.image_name, image.deployment.campaign.short_name, 
                                        image.deployment.short_name, image.position, 
                                        (str(point.x) + ' , ' + str(point.y)), 
                                        point.annotation_caab_code, code_name])
                elif annotation_set_type == 1:                    
                    whole_set = WholeImageAnnotationResource().obj_get_list(bundle, image=image.id)
                    for whole in whole_set: 
                        code_name = ''
                        if whole.annotation_caab_code and whole.annotation_caab_code is not u'':
                            code = AnnotationCodes.objects.filter(caab_code=whole.annotation_caab_code)                    
                            if code and code is not None and len(code) > 0:
                                code_name = code[0].code_name
                        writer.writerow(['Whole Image', image.image_name, image.deployment.campaign.short_name, 
                                        image.deployment.short_name, image.position, '',                                         
                                        whole.annotation_caab_code, code_name])
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
        point_sampling_methodology = json_data['point_sampling_methodology']
        point_sample_size = json_data['point_sample_size']
        annotation_set_type = json_data['annotation_set_type']

        #only proceed with all parameters
        if (name and description and deployment_id and image_sampling_methodology and
            image_sample_size and point_sampling_methodology and point_sample_size) is not None:

            #get the images we are interested in
            image_bundle = Bundle()
            image_bundle.request = request
            image_bundle.data = dict(deployment=deployment_id)

            images = []

            # If deployment_id is a list we'll need to iterate through to build the image list otherwise
            # we've just been given a single deployment ID

            if isinstance(deployment_id,basestring):
                images.extend(ImageResource().obj_get_list(image_bundle, deployment=deployment_id))
            else:
                for deployment in deployment_id:
                    print deployment
                    images.extend(ImageResource().obj_get_list(image_bundle, deployment=deployment))

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
                                              point_sampling_methodology=point_sampling_methodology,
                                              point_sample_size=point_sample_size, 
                                              images=image_subset,
                                              annotation_set_type=annotation_set_type)
            
            AnnotationSetResource().obj_create(annotation_set_bundle)

            # build up a response with a 'Location', so the client knows the project id which is created
            kwargs = dict (resource_name=self._meta.resource_name,
                            pk=new_project.obj.id,
                            api_name=self._meta.api_name)

            response = HttpResponse(content_type='application/json')
            response['Location'] = self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)
            return response

        return self.create_response(request, "Not all fields were provided.", response_class=HttpBadRequest)

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
        bundle.data['permissions'] = get_perms(get_real_user_object(bundle.request.user), bundle.obj)

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
            'annotation_set_type' : 'exact'
        }

    def prepend_urls(self):
        return [            
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/images%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_images'), name="api_get_images"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/similar_images%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_similar_images'), name="api_get_similar_images"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/copy_wholeimage_classification%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('copy_wholeimage_classification'), name="api_copy_wholeimage_classification")
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

    def get_similar_images(self, request, **kwargs):
        """
        This is a helper function which calls the external Lire service to find the similar images. The reason
        we are using a wrapper here is so we don't have to use a proxy, and also to bundle up the image response
        in the standard tastypie/backbone way.
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
        # extract only the images that have blank annotation lables
        path_dict = {}
        image_paths = ""
        for image in annotation_set_images:

            #get the labels for the image
            annotations = WholeImageAnnotation.objects.filter(annotation_set=obj, image=image)

            #check if all the labels are blank
            all_blank = True
            for annotation in annotations:
                #if string is empty
                if len(annotation.annotation_caab_code) != 0:
                    all_blank = False

            # if they are all blank, add the image to the list
            if all_blank:
                image_path = ImageManager().get_image_path(image)
                image_paths += image_path + ","
                path_dict[image_path] = image

        # strip the comma from the end
        image_paths = image_paths[:-1]

        #get the path of the image we want to search with
        image_id = request.GET["image"]
        image_path = ImageManager().get_image_path(Image.objects.get(id=image_id))

        #build the payload
        payload = {"imagePath": image_path, "limit": "12", "similarityGreater": "0.9", "featureType": "cedd", "imageComparisonList": image_paths}

        #make the call
        the_response = requests.post(settings.DOLLY_SEARCH_URL, data=payload)

        #parse the response and get the image paths
        similar_image_list = the_response.json()

        image_ids = ""
        for item in similar_image_list:
            image_ids += path_dict[item["path"]].id.__str__() + ","
        # strip the comma from the end
        image_ids = image_ids[:-1]

        #get the images from the image resource now
        return ImageResource().get_list(request, id__in=image_ids)

    def copy_wholeimage_classification(self, request, **kwargs):
        """
        This is a helper function for copying the whole image annotations from one image, to another image in the
        annotation set.
        """

        # need to create a bundle for tastypie
        basic_bundle = self.build_bundle(request=request)

        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI.")

        #get the path of the image we want to search with
        source_image = request.GET["source_image"]
        destination_image = request.GET["destination_image"]

        #check we have everything
        if len(destination_image) == 0 or len(source_image) == 0:
            return self.create_response(request, "Not all fields were provided.", response_class=HttpBadRequest)

        # get whole image annotations for the source image
        source_image_annotations = WholeImageAnnotation.objects.filter(annotation_set=obj.pk, image=source_image)

        # get whole image annotations for the destination image
        destination_image_annotations = WholeImageAnnotation.objects.filter(annotation_set=obj.pk, image=destination_image)

        # delete the whole image annotations for the destination image
        for annotation in destination_image_annotations:
            WholeImageAnnotationResource().delete_detail(request, id=annotation.id)

        #get tastypie friendly references
        #annotation_set_bundle = AnnotationSetResource().obj_get(basic_bundle, id=obj.pk)
        #destination_image_bundle = ImageResource().obj_get(basic_bundle, id=destination_image)

        annotation_set_bundle = AnnotationSet.objects.get(id=obj.pk)
        destination_image_bundle = Image.objects.get(id=destination_image)

        print annotation_set_bundle
        print destination_image_bundle

        # replace the annotations for the destination image
        for annotation in source_image_annotations:

            annotation_bundle = Bundle()
            annotation_bundle.request = request
            annotation_bundle.data = dict(annotation_set=annotation_set_bundle,
                                          image=destination_image_bundle,
                                          annotation_caab_code=annotation.annotation_caab_code,
                                          qualifier_short_name=annotation.qualifier_short_name,
                                          )
            WholeImageAnnotationResource().obj_create(annotation_bundle)

        # everything went well
        return self.create_response(request, "Copied whole broad scale classifications succesfully.")

    def do_point_sampling_operations(self, bundle):
        """ Helper function to hold all the sampling logic """

        # subsample points based on methodologies
        #bundle.obj.images = bundle.data['image_subset']
        point_sample_size = bundle.data['point_sample_size']
        point_sampling_methodology = bundle.data['point_sampling_methodology']
        
        if point_sampling_methodology == '0':
            PointAnnotationManager().apply_random_sampled_points(bundle.obj, point_sample_size)
        else:
            raise Exception("Point sampling method not implemented.")


    def do_whole_image_point_operations(self, bundle):
        """ Helper function to hold whole image point assignment logic """
        WholeImageAnnotationManager().apply_whole_image_points(bundle.obj)


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

        # generate anootation points
        if int(bundle.data['annotation_set_type']) == 0:
            try:
                self.do_point_sampling_operations(bundle)
            except Exception:
                #delete the object that was created
                bundle.obj.delete()

                #return not implemented response
                raise ImmediateHttpResponse(HttpNotImplemented("Unable to create point (fine scale) annotation set."))
        elif int(bundle.data['annotation_set_type']) == 1:
            try:
                self.do_whole_image_point_operations(bundle)
            except Exception:
                #delete the object that was created
                bundle.obj.delete()

                #return not implemented response
                raise ImmediateHttpResponse(HttpNotImplemented("Unable to create whole image (broad scale) annotation set."))
        else:
            raise ImmediateHttpResponse(HttpNotImplemented("Unexpected annotation set request."))

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

        #attach current user as the owner
        bundle.data['owner'] = user

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
        detail_allowed_methods = ['get', 'post', 'put', 'delete','patch']
        list_allowed_methods = ['get', 'post', 'put', 'delete','patch']
        filtering = {
            'image': ALL,
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

        #attach current user as the owner
        bundle.data['owner'] = user

        super(WholeImageAnnotationResource, self).obj_create(bundle)

        # NOTE: we can't check permissions on related objects until the bundle
        # is created - django throws an exception. What we need to do here is
        # check permissions. If the user does not have permissions we delete
        # the create object.
        if not user.has_perm('projects.change_annotationset', bundle.obj.annotation_set):
            bundle.obj.delete()

        return bundle

    def dehydrate(self, bundle):
        # Add an caab_name field to WholeImageAnnotationResource.
        code_name = ''
        code = bundle.data['annotation_caab_code']
        if code and code is not u'':
            annotation_code = AnnotationCodes.objects.filter(caab_code=code)
            if annotation_code and annotation_code is not None and len(annotation_code) > 0:
                code_name = annotation_code[0].code_name
        bundle.data['annotation_caab_name'] = code_name
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
