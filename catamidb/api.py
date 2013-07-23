from shutil import copy
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms, get_perms)
from tastypie import fields
from tastypie.authentication import (MultiAuthentication,
                                     SessionAuthentication,
                                     ApiKeyAuthentication,
                                     Authentication,
                                     BasicAuthentication)
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized, ImmediateHttpResponse
from tastypie import http
from tastypie.resources import ModelResource, Resource
from .models import *
from catamidb import authorization

import os, sys, shutil
import PIL

import logging

logger = logging.getLogger(__name__)

# ==============================
# Auth configuration for the API
# ==============================

#need this because guardian lookups require the actual django user object
def get_real_user_object(tastypie_user_object):
    # blank username is anonymous
    if tastypie_user_object.is_anonymous():
        user = guardian.utils.get_anonymous_user()
    else:  # if not anonymous, get the real user object from django
        user = User.objects.get(id=tastypie_user_object.id)

    #send it off
    return user


# Used to allow authent of anonymous users for GET requests
class AnonymousGetAuthentication(SessionAuthentication):
    def is_authenticated(self, request, **kwargs):
        # let anonymous users in for GET requests - Authorisation logic will
        # stop them from accessing things not allowed to access
        if request.user.is_anonymous() and request.method == "GET":
            return True

        return super(AnonymousGetAuthentication, self).is_authenticated(
            request, **kwargs)


class CampaignAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        user_objects = get_objects_for_user(user, ['catamidb.view_campaign'],
                                            object_list)

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        logger.debug("In create list")
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        #Allow creates for Authorised users
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class GenericDeploymentAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all deployments for the above allowable campaigns
        deployments = GenericDeployment.objects.select_related("campaign")
        deployment_ids = (deployments.filter(campaign__in=campaign_objects).
                          values_list('id'))

        #now filter out the deployments we are not allowed to see
        return object_list.filter(id__in=deployment_ids)

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class GenericImageAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all images for the above allowable campaigns
        images = GenericImage.objects.select_related("deployment__campaign")
        image_ids = images.filter(
            deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the images we are not allowed to see
        image_objects = object_list.filter(id__in=image_ids)

        # send em off
        return image_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign',
                         bundle.obj.deployment.campaign):
            return True

        print "should not see this"

        raise Unauthorized()

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class ImageUploadAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return image_objects

    def read_detail(self, object_list, bundle):
        return True

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class GenericCameraAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # campaign contain deployments, which is referenced in images. Find images user can see first
        images = GenericImage.objects.select_related("deployment__campaign")
        #get ids of allowed images
        allowed_images_ids = images.filter(
            deployment__campaign__in=campaign_objects).values_list('id')     

        #now filter out the measurements we are not allowed to see   
        return object_list.filter(image__in=allowed_images_ids)
    
    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)
       
        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # campaign contain deployments, which is referenced in images. Find images user can see first
        images = GenericImage.objects.select_related("deployment__campaign")
        #get ids of allowed images
        allowed_images_ids = images.filter(
            deployment__campaign__in=campaign_objects).values_list('id')     

        #now filter out the measurements we are not allowed to see   
        cameras = object_list.filter(image__in=allowed_images_ids)

        # check the user has permission to view this camera
        if bundle.obj in cameras:
            return True

        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class MeasurementsAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # campaign contain deployments, which is referenced in images. Find images user can see first
        images = GenericImage.objects.select_related("deployment__campaign")
        #get ids of allowed images
        allowed_images_ids = images.filter(
            deployment__campaign__in=campaign_objects).values_list('id')     

        #now filter out the measurements we are not allowed to see   
        return object_list.filter(image__in=allowed_images_ids)

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)
       
        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # campaign contain deployments, which is referenced in images. Find images user can see first
        images = GenericImage.objects.select_related("deployment__campaign")
        #get ids of allowed images
        allowed_images_ids = images.filter(
            deployment__campaign__in=campaign_objects).values_list('id')     

        #now filter out the measurements we are not allowed to see   
        measurements = object_list.filter(image__in=allowed_images_ids)  

        # check the user has permission to view the measurements
        if bundle.obj in measurements:
            return True

        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


# ========================
# API configuration
# ========================


class CampaignResource(ModelResource):
    class Meta:
        always_return_data = True,
        queryset = Campaign.objects.all()
        resource_name = "campaign"
        authentication = MultiAuthentication(SessionAuthentication(),
                                             AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = CampaignAuthorization()
        filtering = {
            'short_name': ALL,
            'date_start': ALL,
        }

        allowed_methods = ['get', 'post']  # allow post to create campaign via Backbonejs
        object_class = Campaign

    def hydrate(self, bundle):
        bundle.obj = Campaign()
        return bundle

    def obj_create(self, bundle, **kwargs):
        """
        We are overiding this function so we can get access to the newly
        created campaign. Once we have reference to it, we can apply
        object level permissions to the object.
        """

        # get real user
        user = get_real_user_object(bundle.request.user)

        #create the bundle
        super(CampaignResource, self).obj_create(bundle)

        #make sure we apply permissions to this newly created object
        authorization.apply_campaign_permissions(user, bundle.obj)

        return bundle

    def dehydrate(self, bundle):                   
        dps = GenericDeployment.objects.filter(campaign=bundle.obj.id)
        bundle.data['deployment_count'] = len(dps)
        return bundle

class GenericDeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        always_return_data = True,
        queryset = GenericDeployment.objects.prefetch_related("campaign").all()
        resource_name = "generic_deployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = GenericDeploymentAuthorization()
        filtering = {
            'short_name': ALL,
            'campaign': ALL_WITH_RELATIONS,
            'type' : ALL,
        }
        allowed_methods = ['get', 'post']  # allow post to create campaign via Backbonejs

    def dehydrate(self, bundle):
        #may have more than one deployment pointing to the same campaign, but grab 1st instance
        #as we only want to obtain campaign info.
        dp = self.Meta.queryset.filter(id=bundle.data['id'])[0]; 
        bundle.data['campaign_name'] = dp.campaign.short_name

        # Add the map_extent of all the images in this project
        images = GenericImage.objects.filter(deployment=bundle.obj.id)
        map_extent = ""
        if len(images) != 0:
            map_extent = images.extent().__str__()

        bundle.data['map_extent'] = map_extent

        return bundle


class ImageUploadResource(ModelResource):
    img = fields.FileField(attribute="img", null=True, blank=True)

    class Meta:
        always_return_data = True
        queryset = ImageUpload.objects.all()
        deployments = GenericDeployment.objects.all()
        resource_name = "image_upload"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = ImageUploadAuthorization()
        filtering = {
            'collection': ALL,
        }
        allowed_methods = ['get', 'post']  # allow post to create campaign via Backbonejs

    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(ImageUploadResource, self).deserialize(request, data, format)

    def obj_create(self, bundle, **kwargs):
        if ("img" in bundle.data.keys() and "deployment" in bundle.data.keys()):
            #Split image name and image path
            sourcePath, imgName = os.path.split(str(bundle.data["img"]))
            if imgName.find("@") != -1:
                imgName = imgName[:1]  # remove "@" if exists

            # split image name and image extension

            imgNameNoExt, imgExt = os.path.splitext(imgName)

            if (imgExt.lower() == ".png" or imgExt.lower() == ".jpg" or imgExt.lower() == ".jpeg"):

                deployment = self.Meta.deployments.filter(id=int(bundle.data["deployment"]))

                # Use specified deployment id to get Campaign and Deployment names, which is used to create path for image and thumbnails

                if deployment.exists():
                    deploymentName = deployment[0].short_name
                    campaignName = deployment[0].campaign.short_name

                    # django does like us to write files outside MEDIA_ROOT using djanjo functions,
                    # so we create the image in MEDIA_ROOT and then move it to the desired location (deloymeent directory)

                    temp_dir = os.path.join(settings.MEDIA_ROOT, 'import_temp')

                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    dp = deploymentName + "__" + bundle.data["deployment"]
                    imageDest = os.path.join(settings.IMPORT_PATH, campaignName, dp, "images", "")
                    thumbDest = os.path.join(settings.IMPORT_PATH, campaignName, dp, "thumbnails", "")
                    bundle.obj.img.field.upload_to = temp_dir

                    if not os.path.exists(imageDest):
                        logger.debug("Created directory for images: %s" % imageDest)
                        os.makedirs(imageDest)

                    super(ImageUploadResource, self).obj_create(bundle, **kwargs)

                    shutil.move(os.path.join(temp_dir, imgName), imageDest)

                    logger.debug("%s uploaded to server.." % imgName)
                    size = str(settings.THUMBNAIL_SIZE[0]) + "x" + str(settings.THUMBNAIL_SIZE[1])

                    infile = os.path.normpath(imageDest + imgName)
                    outfile = os.path.normpath(thumbDest + imgNameNoExt + "_" + size + imgExt)

                    logger.debug("Full size image is %s" % infile)
                    logger.debug("Thumbnail image will be %s" % outfile)

                    try:
                        if not os.path.exists(thumbDest):
                            os.makedirs(thumbDest)
                        im = PIL.Image.open(infile)
                        im.thumbnail(settings.THUMBNAIL_SIZE, PIL.Image.ANTIALIAS)
                        im.save(outfile, "JPEG")
                        logger.debug("Thumbnail imagery %s created." % outfile)
                    except IOError:
                        logger.debug("Cannot create thumbnail for '%s'" % infile)
                        raise ImmediateHttpResponse(response=http.HttpBadRequest("Cannot create thumbnail for '%s'" % infile))

                    #Final check to see if thumbnail and image is generated/uploaded respectively.
                    if os.path.isfile(outfile): 
                        try: open(outfile)
                        except IOError:
                            raise ImmediateHttpResponse(response=http.HttpBadRequest("Generated thumbnail missing! '%s'" % outfile))
                    else:
                        raise ImmediateHttpResponse(response=http.HttpBadRequest("Generated thumbnail missing! '%s'" % outfile))
                    if os.path.isfile(infile): 
                        try: open(infile)
                        except IOError:
                            raise ImmediateHttpResponse(response=http.HttpBadRequest("Imported image missing! '%s'" % infile))
                    else:
                        raise ImmediateHttpResponse(response=http.HttpBadRequest("Imported image missing! '%s'" % infile))

                else:
                    raise ImmediateHttpResponse(response=http.HttpBadRequest("Invalid Deployment ID specified:"+str(bundle.data["deployment"])))
            else:
                    raise ImmediateHttpResponse(response=http.HttpBadRequest("Image format not supported! Supported images include .png, .jpg, .jpeg"))
        else:
            raise ImmediateHttpResponse(response=http.HttpBadRequest("Please specify 'img', 'deployment' and 'thumbnailsize' parameters"))
        return bundle


class GenericImageResource(ModelResource):   
    deployment = fields.ToOneField('catamidb.api.GenericDeploymentResource', 'deployment')

    class Meta:
        always_return_data = True
        queryset = GenericImage.objects.all()
        resource_name = "generic_image"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = GenericImageAuthorization()
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'date_time': ALL,
            'id': ALL
        }
        allowed_methods = ['get', 'post'] #allow post to create campaign via Backbonejs

    #this gets called just before sending response. Careful as we are overwritting the method defined in BackboneCompaitibleResource
    def alter_list_data_to_serialize(self, request, data):

        #if flot is asking for the data, we need to package it up a bit
        if request.GET.get("output") == "flot":
            return self.package_series_for_flot_charts(data)

        return data

    #flot takes a two dimensional array of data, so we need to package the
    #series up in this manner
    def package_series_for_flot_charts(self, data):
        data_table = []

        #scale factors for reducing the data
        list_length = len(data['objects'])
        scale_factor = 4

        #for index, bundle in enumerate(data['objects']):
        #    data_table.append([index, bundle.obj.value])
        for i in range(0, list_length, scale_factor):
            data_table.append([i, data['objects'][i].data['depth']])

        return {'data': data_table}


    def dehydrate(self, bundle):
        deploymentName = bundle.obj.deployment.short_name
        campaignName = bundle.obj.deployment.campaign.short_name
        imageName = bundle.obj.image_name
        imgNameNoExt, imgExt = os.path.splitext(imageName)
        size = str(settings.THUMBNAIL_SIZE[0]) + "x" + str(settings.THUMBNAIL_SIZE[1])
        thumbnailName = imgNameNoExt + "_" + size + imgExt        
        bundle.data['web_location'] = "http://" + bundle.request.get_host() + "/images/" + campaignName + "/" + deploymentName + "/images/" + imageName
        bundle.data['thumbnail_location'] = "http://" + bundle.request.get_host() + "/images/" + campaignName + "/" + deploymentName + "/thumbnails/" + thumbnailName
        return bundle


class GenericCameraResource(ModelResource):   
    image = fields.ToOneField('catamidb.api.GenericImageResource', 'image')    
    class Meta:
        always_return_data = True
        queryset = GenericCamera.objects.all()
        resource_name = "generic_camera"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = GenericCameraAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
        }
        allowed_methods = ['get', 'post'] #allow post to create campaign via Backbonejs


class MeasurementsResource(ModelResource):     
    image = fields.ToOneField('catamidb.api.GenericImageResource', 'image')   
    class Meta:
        always_return_data = True
        queryset = Measurements.objects.all()
        resource_name = "measurements"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = MeasurementsAuthorization()
        filtering = {
            'image': ALL,
            'temperature': ALL,
            'salinity': ALL,
            'pitch': ALL,
            'roll': ALL,
            'yaw': ALL,
            'altitude': ALL,
            'id': ALL,
        }
        allowed_methods = ['get', 'post'] #allow post to create campaign via Backbonejs
        filtering = {
            'image': ALL_WITH_RELATIONS,
        }

    #this gets called just before sending response. Careful as we are overwritting the method defined in BackboneCompaitibleResource
    def alter_list_data_to_serialize(self, request, data):

        #if flot is asking for the data, we need to package it up a bit
        if request.GET.get("output") == "flot":
            return self.package_series_for_flot_charts(data, request.GET.get("mtype"))

        return data

    #flot takes a two dimensional array of data, so we need to package the
    #series up in this manner
    def package_series_for_flot_charts(self, data, mtype):
        data_table = []

        #filter by measurement type
        list_length = len(data['objects'])
        filtered_table = []
        for i in range(0, list_length,1):
            if data['objects'][i].data[mtype] is not None:
                filtered_table.append(data['objects'][i].data[mtype])

        #scale factors for reducing the data
        filtered_length = len(filtered_table)
        scale_factor = 4

        #for index, bundle in enumerate(data['objects']):
        #    data_table.append([index, bundle.obj.value])
        for i in range(0, filtered_length, scale_factor):
            data_table.append([i, filtered_table[i]])

        return {'data': data_table}