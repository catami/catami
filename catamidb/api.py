from shutil import copy
from django.contrib.auth.models import User
import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms)
from tastypie import fields
from tastypie.authentication import (MultiAuthentication,
                                     SessionAuthentication,
                                     ApiKeyAuthentication,
                                     Authentication,
                                     BasicAuthentication)
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, Resource
from .models import *
from restthumbnails.helpers import get_thumbnail_proxy




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
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
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
        deployment_objects = object_list.filter(id__in=deployment_ids)

        # send em off
        return deployment_objects

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


class PoseAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all poses for the above allowable campaigns
        poses = Pose.objects.select_related("deployment__campaign")
        pose_ids = (poses.filter(deployment__campaign__in=campaign_objects).
                    values_list('id'))

        #now filter out the poses we are not allowed to see
        pose_objects = object_list.filter(id__in=pose_ids)

        # send em off
        return pose_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign',
                         bundle.obj.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
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


class ImageAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all images for the above allowable campaigns
        images = Image.objects.select_related("pose__deployment__campaign")
        image_ids = images.filter(
            pose__deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the images we are not allowed to see
        image_objects = object_list.filter(id__in=image_ids)

        # send em off
        return image_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign',
                         bundle.obj.pose.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
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


class ScientificPoseMeasurementAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all measurements for the above allowable campaigns
        measurements = ScientificPoseMeasurement.objects.select_related(
            "pose__deployment__campaign")
        measurement_ids = measurements.filter(
            pose__deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the measurements we are not allowed to see
        measurement_objects = object_list.filter(id__in=measurement_ids)

        # send em off
        return measurement_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign',
                         bundle.obj.pose.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
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


class ScientificImageMeasurementAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        campaign_objects = get_objects_for_user(user, [
            'catamidb.view_campaign'])

        # get all measurements for the above allowable campaigns
        measurements = ScientificImageMeasurement.objects.select_related(
            "image__pose__deployment__campaign")
        measurements2 = measurements.filter(
            image__pose__deployment__campaign__in=campaign_objects)
        measurement_ids = measurements2.values_list('id')

        #now filter out the measurements we are not allowed to see
        measurement_objects = object_list.filter(id__in=measurement_ids)

        # send em off
        return measurement_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.image.pose.
        deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
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

# ========================
# API configuration
# ========================

class CampaignResource(ModelResource):
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = "campaign"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = CampaignAuthorization()
        allowed_methods = ['get']

class DeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        queryset = Deployment.objects.prefetch_related("campaign").all()
        resource_name = "deployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        filtering = {
            'campaign': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']


class PoseResource(ModelResource):
    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    images = fields.ToManyField('catamidb.api.ImageResource', 'image_set',full=True)
    measurements = fields.ToManyField(
        'catamidb.api.ScientificPoseMeasurementResource',
        'scientificposemeasurement_set')

    class Meta:
        queryset = Pose.objects.all()
        resource_name = "pose"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = PoseAuthorization()
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'depth': ['range', 'gt', 'lt', 'gte', 'lte'],
        }
        allowed_methods = ['get']


    def dehydrate_measurements(self, bundle):
        # change to view a small subset of the info
        # the rest isn't really needed in this resource
        outlist = []
        for m in bundle.data['measurements']:
            outitem = {}
            outitem['value'] = m.data['value']
            outitem['units'] = m.data['mtype'].data['units']
            outitem['name'] = m.data['mtype'].data['display_name']
            outlist.append(outitem)

        return outlist

        #return bundle


    def dehydrate_images(self, bundle):
        """Dehydrate images within a pose.

        This override is to remove the pose uri field as it
        is redundant when included as part of a pose.
        """
        outlist = []
        for image in bundle.data['images']:
            outimage = dict(image.data)

            del outimage['pose']
            outlist.append(outimage)

        return outlist

class ImageResource(ModelResource):
    pose = fields.ForeignKey(PoseResource, 'pose')
    measurements = fields.ToManyField(
        'catamidb.api.ScientificImageMeasurementResource',
        'scientificimagemeasurement_set')
    collection = fields.ToManyField('collection.api.CollectionResource',
                                    'collections')

    class Meta:
        queryset = Image.objects.prefetch_related("pose").all()
        resource_name = "image"
        excludes = ['archive_location']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = ImageAuthorization()
        filtering = {
            'pose': ALL_WITH_RELATIONS,
            'collection': ALL,

        }
        allowed_methods = ['get']

    def dehydrate_measurements(self, bundle):
        # change to view a small subset of the info
        # the rest isn't really needed in this resource
        outlist = []
        for m in bundle.data['measurements']:
            outitem = {}
            outitem['value'] = m.data['value']
            outitem['units'] = m.data['mtype'].data['units']
            outitem['name'] = m.data['mtype'].data['display_name']

            outlist.append(outitem)

        return outlist

    def dehydrate(self, bundle):
        file_name = bundle.data['web_location']
        bundle.data['thumbnail_location'] = get_thumbnail_proxy(
            file_name,
            "96x72",
            'scale',
            '.jpg'
        ).url
        bundle.data['web_location'] = 'images/{0}'.format(file_name)
        return bundle

    def get_object_list(self, request):
        images = super(ImageResource, self).get_object_list(request)

        #get the ranges to query on
        temperature__gte = request.GET.get("temperature__gte")
        temperature__lte = request.GET.get("temperature__lte")

        salinity__gte = request.GET.get("salinity__gte")
        salinity__lte = request.GET.get("salinity__lte")

        altitude__gte = request.GET.get("altitude__gte")
        altitude__lte = request.GET.get("altitude__lte")

        # get the measurement types we want to query
        measurement_types = ScientificMeasurementType.objects.all()
        temperature = measurement_types.get(normalised_name="temperature")
        salinity = measurement_types.get(normalised_name="salinity")
        altitude = measurement_types.get(normalised_name="altitude")

        #filter temperature
        if temperature__lte is not None and temperature__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=temperature, pose__scientificposemeasurement__value__range=(temperature__gte, temperature__lte))

        #then filter out salinity - chain
        if salinity__lte is not None and salinity__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=salinity, pose__scientificposemeasurement__value__range=(salinity__gte, salinity__lte))

        #then filter out altitude - chain
        if altitude__lte is not None and altitude__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=altitude, pose__scientificposemeasurement__value__range=(altitude__gte, altitude__lte))

        return images

class ScientificMeasurementTypeResource(ModelResource):
    class Meta:
        queryset = ScientificMeasurementType.objects.all()
        resource_name = "scientificmeasurementtype"
        allowed_methods = ['get']
        filtering = {
            'normalised_name': ALL,
        }

class SimplePoseResource(ModelResource):
    """
        SimplePoseResource has very limited relations. This is used for
        performance purposes. i.e. Directly querying this resource should
        be fast-ish...
    """

    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    #images = fields.ToManyField('catamidb.api.ImageResource', 'image_set',full=True)
    #measurements = fields.ToManyField(
    #    'catamidb.api.ScientificPoseMeasurementResource',
    #    'scientificposemeasurement_set')

    class Meta:
        queryset = Pose.objects.prefetch_related("deployment").all()
        resource_name = "simplepose"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = PoseAuthorization()
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'depth': ['range', 'gt', 'lt'],
            }
        allowed_methods = ['get']

    #this gets called just before sending response
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

class ScientificPoseMeasurementResource(ModelResource):

    #this pose is related to the SimplePoseResource for performance pruposes
    pose = fields.ToOneField(SimplePoseResource, 'pose')
    mtype = fields.ToOneField(ScientificMeasurementTypeResource, "measurement_type")

    class Meta:
        queryset = ScientificPoseMeasurement.objects.prefetch_related("pose")\
            .prefetch_related("measurement_type").all()
        resource_name = "scientificposemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = ScientificPoseMeasurementAuthorization()
        filtering = {
            'pose': ALL_WITH_RELATIONS,
            'mtype': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']

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
            data_table.append([i, data['objects'][i].data['value']])

        return {'data': data_table}

class ScientificImageMeasurementResource(ModelResource):
    image = fields.ToOneField('catamidb.api.ImageResource', 'image')

    class Meta:
        queryset = ScientificImageMeasurement.objects.all()
        resource_name = "scientificimagemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = ScientificImageMeasurementAuthorization()
        filtering = {
            'image': 'exact',
        }
        allowed_methods = ['get']


class AUVDeploymentResource(ModelResource):
    class Meta:
        queryset = AUVDeployment.objects.all()
        resource_name = "auvdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']


class BRUVDeploymentResource(ModelResource):
    class Meta:
        queryset = BRUVDeployment.objects.all()
        resource_name = "bruvdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']


class DOVDeploymentResource(ModelResource):
    class Meta:
        queryset = DOVDeployment.objects.all()
        resource_name = "dovdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']
