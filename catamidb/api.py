from shutil import copy
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse
from django.utils import simplejson
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms, get_perms)
from tastypie import fields
from tastypie.utils import trailing_slash
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
from tastypie.bundle import Bundle
from .models import *
from catamidb import authorization

import os, shutil
import PIL
import json
import codecs

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


class DeploymentAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all deployments for the above allowable campaigns
        deployments = Deployment.objects.select_related("campaign")
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


class ImageAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all images for the above allowable campaigns
        images = Image.objects.select_related("deployment__campaign")
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


class CameraAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # campaign contain deployments, which is referenced in images. Find images user can see first
        images = Image.objects.select_related("deployment__campaign")
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
        images = Image.objects.select_related("deployment__campaign")
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
        images = Image.objects.select_related("deployment__campaign")
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
        images = Image.objects.select_related("deployment__campaign")
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
        dps = Deployment.objects.filter(campaign=bundle.obj.id)
        bundle.data['deployment_count'] = len(dps)
        return bundle


class DeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        always_return_data = True,
        queryset = Deployment.objects.prefetch_related("campaign").all()
        resource_name = "deployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
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
        images = Image.objects.filter(deployment=bundle.obj.id)
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
        deployments = Deployment.objects.all()
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
        if format == 'application/x-www-form-urlencoded; charset=UTF-8':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)
            return data
        return super(ImageUploadResource, self).deserialize(request, data, format)

    def obj_create(self, bundle, **kwargs):

        if ("img" in bundle.data.keys() and "deployment" in bundle.data.keys()):

            imageName = str(bundle.data["img"])
            sourcePath, imgName = os.path.split(imageName)
            if imgName.find("@") != -1:
                imgName = imgName[:1]  # remove "@" if exists
            # split image name and image extension
            imgNameNoExt, imgExt = os.path.splitext(imageName)
            if (imgExt.lower() == ".png" or imgExt.lower() == ".jpg" or imgExt.lower() == ".jpeg"):

                deployment = self.Meta.deployments.filter(id=int(bundle.data["deployment"]))            
                if deployment.exists():
                    # django does like us to write files outside MEDIA_ROOT using djanjo functions,
                    # so we create the image in MEDIA_ROOT and then move it to the desired location (deloymeent directory)
                    temp_dir = os.path.join(settings.MEDIA_ROOT, 'import_temp')

                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)                   
                    imageDest = ImageManager().get_image_destination(deployment[0], settings.IMPORT_PATH)
                    thumbDest = ImageManager().get_thumbnail_destination(deployment[0], settings.IMPORT_PATH)

                    if ("filedata" in bundle.data.keys()):
                        #write filedata Blob() to image as named in temp_dir
                        path = default_storage.save(os.path.join(temp_dir, imgName), ContentFile(bundle.data["filedata"].read()))
                    else :
                        bundle.obj.img.field.upload_to = temp_dir

                    if not os.path.exists(imageDest):
                        logger.debug("Created directory for images: %s" % imageDest)
                        os.makedirs(imageDest)                                     
                    
                    super(ImageUploadResource, self).obj_create(bundle, **kwargs)
                    try:
                        src = os.path.join(temp_dir, imgName)
                        if not os.path.isfile(os.path.join(imageDest, imgName)) :
                            shutil.move(src, imageDest)
                        else :
                            logger.debug("File %s exists! Overwriting" % imgName)
                            shutil.copy(src, imageDest)
                            os.remove(src)                            
                    except IOError:
                        logger.debug("Unable to move file '%s' to %s" % (imgName, imageDest) )
                    logger.debug("%s uploaded to server.." % imgName)
                                                         
                    infile = ImageManager().get_image_location(imageDest, imgName) 
                    outfile = ImageManager().get_thumbanail_location(thumbDest, imgName, settings.THUMBNAIL_SIZE)

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
                            raise ImmediateHttpResponse(response=http.HttpBadRequest("Unable to open generated thumbnail! '%s'" % outfile))
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


class ImageResource(ModelResource):
    deployment = fields.ToOneField('catamidb.api.DeploymentResource', 'deployment')

    class Meta:
        always_return_data = True
        queryset = Image.objects.all().order_by('date_time')
        resource_name = "image"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = ImageAuthorization()
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'date_time': ALL,
            'id': ALL
        }
        # patch and put added to permit bulk posting via patch_list
        allowed_methods = ['get', 'post', 'patch', 'put'] #allow post to create campaign via Backbonejs

    def prepend_urls(self):
        return [
            url(r"^(?P<image>%s)/upload%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('image_upload'), name="image_upload"),
        ]

    def image_upload(self, request, **kwargs):
        """
        Special handler function to create a project based on search criteria from images
        """

        json_data = simplejson.loads(request.body)

        deployments =  []
        logger.debug("starting web based metadata ingest %s" % json_data['objects'][0]['deployment'])

        #pull the query parameters out
        for i in range(0, len(json_data['objects']),1):
            deployment = json_data['objects'][i]['deployment']             
            deployment_id = deployment.split('/')[len(deployment.split('/'))-2]
            #dp = None
            #if deployment_id in deployments.keys():
            #    dp = deployments[deployment_id]
            #else:
            #    dp = Deployment.objects.filter(id=int(deployment_id))


            #create the Image
            image_bundle = Bundle()
            image_bundle.request = request

            image_name = json_data['objects'][i]['image_name']
            date_time = json_data['objects'][i]['date_time']
            position = json_data['objects'][i]['position']
            depth = json_data['objects'][i]['depth']
            depth_uncertainty = json_data['objects'][i]['depth_uncertainty']
            dpc = None
            if (depth_uncertainty is not None and depth_uncertainty != 'null'):    
                dpc = float(depth_uncertainty)           
            image_bundle.data = dict(deployment=deployment, image_name=image_name, 
                                     date_time=date_time, position=position, depth=depth, 
                                     depth_uncertainty=dpc)
            new_image = self.obj_create(image_bundle)   
                  
            #create Measurement
            temperature = json_data['objects'][i]['temperature']
            temperature_unit = json_data['objects'][i]['temperature_unit']
            salinity = json_data['objects'][i]['salinity']
            salinity_unit = json_data['objects'][i]['salinity_unit']
            pitch = json_data['objects'][i]['pitch']
            pitch_unit = json_data['objects'][i]['pitch_unit']
            roll = json_data['objects'][i]['roll']
            roll_unit = json_data['objects'][i]['roll_unit']
            yaw = json_data['objects'][i]['yaw']
            yaw_unit = json_data['objects'][i]['yaw_unit']
            altitude = json_data['objects'][i]['altitude']
            altitude_unit = json_data['objects'][i]['altitude_unit']

            measurement_bundle = Bundle()
            measurement_bundle.request = request
            measurement_bundle.data = dict(image='/api/dev/image/'+str(new_image.obj.id)+'/',
                                           temperature=temperature,
                                           temperature_unit=temperature_unit,
                                           salinity=salinity,
                                           salinity_unit=salinity_unit,
                                           pitch=pitch,
                                           pitch_unit=pitch_unit,
                                           roll=roll,
                                           roll_unit=roll_unit,
                                           yaw=yaw,
                                           yaw_unit=yaw_unit,
                                           altitude=altitude,
                                          altitude_unit=altitude_unit) 

            new_measurement = MeasurementsResource().obj_create(measurement_bundle)   
            
            #create camera
            angle = json_data['objects'][i]['angle']
            name = json_data['objects'][i]['name']

            camera_bundle = Bundle()
            camera_bundle.request = request
            camera_bundle.data = dict(image='/api/dev/image/'+str(new_image.obj.id)+'/',
                                      name=name,
                                      angle=int(angle))

            new_camera = CameraResource().obj_create(camera_bundle) 

            deployment_response = {'image_name': image_name, 'image_uri':'/api/dev/image/'+str(new_image.obj.id)}

            deployments.append(deployment_response)

        logger.debug("finished web based metadata ingest %s" % json_data['objects'][0]['deployment'])

        response = HttpResponse(content_type='application/json')
        response.content = json.dumps(deployments)

        return response

        return self.create_response(request, "Not all fields were provided.", response_class=HttpBadRequest)

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
        deploymentId = str(bundle.obj.deployment.id)
        campaignId = str(bundle.obj.deployment.campaign.id)
        imageName = bundle.obj.image_name
        imgNameNoExt, imgExt = os.path.splitext(imageName)
        size = str(settings.THUMBNAIL_SIZE[0]) + "x" + str(settings.THUMBNAIL_SIZE[1])
        thumbnailName = imgNameNoExt + "_" + size + imgExt        

        location = "http://" + bundle.request.get_host() + "/images/" + campaignId + "/" + deploymentId
        bundle.data['web_location'] = location + "/images/" + imageName
        bundle.data['thumbnail_location'] = location + "/thumbnails/" + thumbnailName
        return bundle


class CameraResource(ModelResource):
    image = fields.ToOneField('catamidb.api.ImageResource', 'image')
    class Meta:
        always_return_data = True
        queryset = Camera.objects.all()
        resource_name = "camera"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = CameraAuthorization()
        filtering = {
            'id': ALL,
            'name': ALL,
        }
        # patch and put added to permit bulk posting via patch_list
        allowed_methods = ['get', 'post','patch','put'] #allow post to create campaign via Backbonejs


class MeasurementsResource(ModelResource):     
    image = fields.ToOneField('catamidb.api.ImageResource', 'image')
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
        # patch and put added to permit bulk posting via patch_list
        allowed_methods = ['get', 'post','patch','put'] #allow post to create campaign via Backbonejs
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