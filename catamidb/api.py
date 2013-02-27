from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from .models import *


class CampaignResource(ModelResource):
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = "campaign"


class DeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        queryset = Deployment.objects.all()
        resource_name = "deployment"
        filtering = {
            'campaign': ALL_WITH_RELATIONS,
        }


class PoseResource(ModelResource):
    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    images = fields.ToManyField('catamidb.api.ImageResource', 'image_set', full=True)
    measurements = fields.ToManyField('catamidb.api.ScientificPoseMeasurementResource', 'scientificposemeasurement_set', full=True)

    class Meta:
        queryset = Pose.objects.all()
        resource_name = "pose"
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
        }

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
        filtering = {
            'pose': ALL_WITH_RELATIONS,
            'collection': ALL,
        }

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


class ScientificPoseMeasurementResource(ModelResource):
    pose = fields.ToOneField('catamidb.api.PoseResource', 'pose')
    mtype = fields.ToOneField('catamidb.api.ScientificMeasurementTypeResource', "measurement_type", full=True)

    class Meta:
        queryset = ScientificPoseMeasurement.objects.all()
        resource_name = "scientificposemeasurement"
        filtering = {
            'pose': 'exact',
        }


class ScientificImageMeasurementResource(ModelResource):
    image = fields.ToOneField('catamidb.models.ImageResource', 'image')

    class Meta:
        queryset = ScientificImageMeasurement.objects.all()
        resource_name = "scientificimagemeasurement"
        filtering = {
            'image': 'exact',
        }


class AUVDeploymentResource(ModelResource):
    class Meta:
        queryset = AUVDeployment.objects.all()
        resource_name = "auvdeployment"


class BRUVDeploymentResource(ModelResource):
    class Meta:
        queryset = BRUVDeployment.objects.all()
        resource_name = "bruvdeployment"


class DOVDeploymentResource(ModelResource):
    class Meta:
        queryset = DOVDeployment.objects.all()
        resource_name = "dovdeployment"
