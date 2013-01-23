from tastypie import fields
from tastypie.resources import ModelResource
from .models import Campaign, Deployment, Image
from .models import AUVDeployment, BRUVDeployment, DOVDeployment

class CampaignResource(ModelResource):
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = "campaign"


class DeploymentResource(ModelResource):
    class Meta:
        queryset = Deployment.objects.all()
        resource_name = "deployment"


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


class ImageResource(ModelResource):
    class Meta:
        queryset = Image.objects.all()
        resource_name = "image"
