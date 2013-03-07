from django.contrib.auth.models import User
import guardian
from guardian.shortcuts import get_objects_for_user, get_perms_for_model, get_users_with_perms, get_groups_with_perms
from tastypie import fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication, ApiKeyAuthentication, Authentication, BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource
from .models import *


# ==============================
# Auth configuration for the API
# ==============================

#need this because guardian lookups require the actual django user object
def get_real_user_object(tastypie_user_object):

    # blank username is anonymous
    if tastypie_user_object.is_anonymous():
        user = guardian.utils.get_anonymous_user()
    else: # if not anonymous, get the real user object from django
        user = User.objects.get(id=tastypie_user_object.id)

    #send it off
    return user

# Used to allow authent of anonymous users for GET requests
class AnonymousGetAuthentication(SessionAuthentication):

    def is_authenticated(self, request, **kwargs):

        # let anonymous users in for GET requests - Authorisation logic will stop them from accessing things not allowed to access
        if request.user.is_anonymous() and request.method == "GET":
            return True

        return super(AnonymousGetAuthentication, self).is_authenticated(request, **kwargs)

class CampaignAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        user_objects = get_objects_for_user(user, ['catamidb.view_campaign'], object_list)

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        campaign_objects = get_objects_for_user(user, ['catamidb.view_campaign'])

        # get all deployments for the above allowable campaigns
        deployments = Deployment.objects.select_related("campaign")
        deployment_ids = deployments.filter(campaign__in=campaign_objects).values_list('id')

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

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        campaign_objects = get_objects_for_user(user, ['catamidb.view_campaign'])

        # get all poses for the above allowable campaigns
        poses = Pose.objects.select_related("deployment__campaign")
        pose_ids = poses.filter(deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the poses we are not allowed to see
        pose_objects = object_list.filter(id__in=pose_ids)

        # send em off
        return pose_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        campaign_objects = get_objects_for_user(user, ['catamidb.view_campaign'])

        # get all images for the above allowable campaigns
        images = Image.objects.select_related("pose__deployment__campaign")
        image_ids = images.filter(pose__deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the images we are not allowed to see
        image_objects = object_list.filter(id__in=image_ids)

        # send em off
        return image_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.pose.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        campaign_objects = get_objects_for_user(user, ['catamidb.view_campaign'])

        # get all measurements for the above allowable campaigns
        measurements = ScientificPoseMeasurement.objects.select_related("pose__deployment__campaign")
        measurement_ids = measurements.filter(pose__deployment__campaign__in=campaign_objects).values_list('id')

        #now filter out the measurements we are not allowed to see
        measurement_objects = object_list.filter(id__in=measurement_ids)

        # send em off
        return measurement_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.pose.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        campaign_objects = get_objects_for_user(user, ['catamidb.view_campaign'])

        # get all measurements for the above allowable campaigns
        measurements = ScientificImageMeasurement.objects.select_related("image__pose__deployment__campaign")
        measurements2 = measurements.filter(image__pose__deployment__campaign__in=campaign_objects)
        measurement_ids = measurements2.values_list('id')

        #now filter out the measurements we are not allowed to see
        measurement_objects = object_list.filter(id__in=measurement_ids)

        # send em off
        return measurement_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('catamidb.view_campaign', bundle.obj.image.pose.deployment.campaign):
            return True

        # raise hell! - https://github.com/toastdriven/django-tastypie/issues/826
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
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = CampaignAuthorization()
        allowed_methods = ['get']

    #def obj_create(self, bundle, request=None, **kwargs):

        # translate JSON object into a campaign object - didn't think I had to do this, but leaving to
        # tastypie caused duplicate key exceptions
#        campaign = Campaign()
#        campaign.short_name = bundle.data["short_name"]
#        campaign.description = bundle.data["description"]
#        campaign.associated_researchers = bundle.data["associated_researchers"]
#        campaign.associated_publications = bundle.data["associated_publications"]
#        campaign.associated_research_grant = bundle.data["associated_research_grant"]
#        campaign.date_start = bundle.data["date_start"]
#        campaign.date_end = bundle.data["date_end"]
#        campaign.contact_person = bundle.data["contact_person"]
#
#        return campaign

    #for POST
#    def obj_create(self, bundle, request, **kwargs):
#        #check permissions first
#        bundle = self._meta.authorization.apply_limits(request, bundle)
#        return super(CampaignResource, self).obj_create(bundle, request, **kwargs)
#
#    #for PUT
#    def obj_update(self, bundle, request, **kwargs):
#        #check permissions first
#        bundle = self._meta.authorization.apply_limits(request, bundle)
#        return super(CampaignResource, self).obj_update(bundle, request, **kwargs)

class DeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        queryset = Deployment.objects.all()
        resource_name = "deployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        filtering = {
            'campaign': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']

class PoseResource(ModelResource):
    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    images = fields.ToManyField('catamidb.api.ImageResource', 'image_set', full=True)
    measurements = fields.ToManyField('catamidb.api.ScientificPoseMeasurementResource', 'scientificposemeasurement_set', full=True)

    class Meta:
        queryset = Pose.objects.all()
        resource_name = "pose"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = PoseAuthorization()
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
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
    measurements = fields.ToManyField('catamidb.api.ScientificImageMeasurementResource', 'scientificimagemeasurement_set')
    collection = fields.ToManyField('collection.api.CollectionResource', 'collections')

    class Meta:
        queryset = Image.objects.all()
        resource_name = "image"
        excludes = ['archive_location']
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
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

class ScientificMeasurementTypeResource(ModelResource):
    class Meta:
        queryset = ScientificMeasurementType.objects.all()
        resource_name = "scientificmeasurementtype"
        allowed_methods = ['get']

class ScientificPoseMeasurementResource(ModelResource):
    pose = fields.ToOneField('catamidb.api.PoseResource', 'pose')
    mtype = fields.ToOneField('catamidb.api.ScientificMeasurementTypeResource', "measurement_type", full=True)

    class Meta:
        queryset = ScientificPoseMeasurement.objects.all()
        resource_name = "scientificposemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = ScientificPoseMeasurementAuthorization()
        filtering = {
            'pose': 'exact',
        }
        allowed_methods = ['get']

class ScientificImageMeasurementResource(ModelResource):
    image = fields.ToOneField('catamidb.api.ImageResource', 'image')

    class Meta:
        queryset = ScientificImageMeasurement.objects.all()
        resource_name = "scientificimagemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = ScientificImageMeasurementAuthorization()
        filtering = {
            'image': 'exact',
        }
        allowed_methods = ['get']


class AUVDeploymentResource(ModelResource):
    class Meta:
        queryset = AUVDeployment.objects.all()
        resource_name = "auvdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']


class BRUVDeploymentResource(ModelResource):
    class Meta:
        queryset = BRUVDeployment.objects.all()
        resource_name = "bruvdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']


class DOVDeploymentResource(ModelResource):
    class Meta:
        queryset = DOVDeployment.objects.all()
        resource_name = "dovdeployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(), ApiKeyAuthentication())
        authorization = DeploymentAuthorization()
        allowed_methods = ['get']

