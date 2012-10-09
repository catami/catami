"""@brief Django views generation (html) for Catami data.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""

# Create your views here.
from django.template import RequestContext
#from django.http import Http404
from django.shortcuts import render_to_response, redirect
#from django.core import serializers
#from django.contrib.gis.geos import GEOSGeometry

from vectorformats.Formats import Django, GeoJSON

from Force.models import Campaign, AUVDeployment,BRUVDeployment, DOVDeployment, Deployment, StereoImage


def index(request):
    """@brief Root html for Catami data

    """
    context = {}

    return render_to_response(
        'Force/index.html',
        context,
        RequestContext(request))


def add_campaign(request):
    """@brief redirect to admin view to create a campaign object

    """

    return redirect('/admin/Force/campaign/add/')  # Redirect after POST


def deployments(request):
    """@brief Deployment list html for entire database

    """
    auv_deployment_list = AUVDeployment.objects.all()
    bruv_deployment_list = BRUVDeployment.objects.all()
    dov_deployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'Force/DeploymentIndex.html',
        {'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list},
        context_instance=RequestContext(request))


def deployments_map(request):
    """@brief Deployment map html for entire database

    """
    latest_deployment_list = Deployment.objects.all()
    return render_to_response(
        'Force/DeploymentMap.html',
        {'latest_deployment_list': latest_deployment_list},
        context_instance=RequestContext(request))


def auvdeployments(request):
    """@brief AUV Deployment list html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'Force/auvDeploymentIndex.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployments_map(request):
    """@brief AUV Deployment map html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'Force/auvDeploymentMap.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployment_detail(request, auvdeployment_id):
    """@brief AUV Deployment html for a specifed AUV deployment

    """
    # the hard way. All columns in the geojson
    #djf=Django.Django(geodjango="transect_shape", properties=[])

    #geoj = GeoJSON.GeoJSON()
    #deployment_as_geojson = geoj.encode(djf.decode([AUVDeployment.objects.get(id=auvdeployment_id)]))

    auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)

    # the easy way is to just return
    # auvdeployment_object.transect_shape.geojson
    return render_to_response(
        'Force/auvdeploymentInstance.html',
        {'auvdeployment_object': auvdeployment_object,
        'deployment_as_geojson': auvdeployment_object.transect_shape.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def campaigns(request):
    """@brief Campaign list html for entire database

    """
    latest_campaign_list = Campaign.objects.all()
    return render_to_response(
        'Force/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list},
        context_instance=RequestContext(request))


def campaign_detail(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """
    campaign_object = Campaign.objects.get(id=campaign_id)
    djf = Django.Django(geodjango="", properties=[])

    auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign_object)
    bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign_object)
    dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign_object)

    geoj = GeoJSON.GeoJSON()
    campaign_as_geojson = geoj.encode(djf.decode([Campaign.objects.get(id=campaign_id)]))

    return render_to_response(
        'Force/campaignInstance.html',
        {'campaign_object': campaign_object,
        'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list,
        'campaign_as_geojson': campaign_as_geojson},
        context_instance=RequestContext(request))
