# Create your views here.
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render, redirect
from Force.forms import CampaignForm
from Force.models import *
from django.core.urlresolvers import reverse
from vectorformats.Formats import Django, GeoJSON
from django.core import serializers
from django.contrib.gis.geos import GEOSGeometry

def index(request):
    return HttpResponse("Hello World, from the CATAMI team.  We are not up and running yet, you can follow us here for now https://plus.google.com/u/0/b/104765819602128308640/104765819602128308640/posts")

def add_campaign(request):
    return redirect('/admin/Force/campaign/add/') # Redirect after POST

def auvdeployments(request):
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response('auvDeploymentIndex.html', {'latest_auvdeployment_list': latest_auvdeployment_list},context_instance=RequestContext(request))
   
def campaigns(request):
    latest_campaign_list = Campaign.objects.all()
    return render_to_response('campaignIndex.html', {'latest_campaign_list': latest_campaign_list},context_instance=RequestContext(request))

def auvdeploymentDetail(request, auvdeployment_id):

    # the hard way. All columns in the geojson
    #djf=Django.Django(geodjango="transect_shape", properties=[])

    #geoj = GeoJSON.GeoJSON()
    #deployment_as_geojson = geoj.encode(djf.decode([AUVDeployment.objects.get(id=auvdeployment_id)]))
    
    auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)

    ## the easy way is to just return auvdeployment_object.transect_shape.geojson
    return render_to_response('auvdeploymentInstance.html', {'auvdeployment_object': auvdeployment_object,'deployment_as_geojson':auvdeployment_object.transect_shape.geojson},context_instance=RequestContext(request))


def campaignDetail(request, campaign_id):
    campaignObject = Campaign.objects.get(id=campaign_id)
    djf=Django.Django(geodjango="", properties=[])

    auvdeployment_list_for_campaign = AUVDeployment.objects.filter(campaign=campaignObject)
    geoj = GeoJSON.GeoJSON()
    campaign_as_geojson = geoj.encode(djf.decode([Campaign.objects.get(id=campaign_id)]))


    return render_to_response('campaignInstance.html', {'campaignObject': campaignObject, 'auvdeployment_list_for_campaign':auvdeployment_list_for_campaign, 'campaign_as_geojson':campaign_as_geojson},context_instance=RequestContext(request))
