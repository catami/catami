from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from .models import Campaign, Deployment, Pose
from .models import AUVDeployment, BRUVDeployment, DOVDeployment


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
            'campaign': ['exact', 'in']
        }



class PoseResource(ModelResource):
    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    images = fields.ToManyField('catamidb.models.ImageResource', 'images', full=True)
    posemeasurements = fields.ToManyField('catamidb.models.ScientificPoseMeasurement', 'posemeasurements')
    class Meta:
        queryset = Pose.objects.all()
        resource_name = "pose"
        filtering = {
            'deployment': 'exact',
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
