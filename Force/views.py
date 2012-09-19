# Create your views here.
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render, redirect
from Force.forms import CampaignForm
from Force.models import *
from django.core.urlresolvers import reverse
from vectorformats.Formats import Django, GeoJSON
from django.core import serializers

def index(request):
    return HttpResponse("Hello World, from the CATAMI team.  We are not up and running yet, you can follow us here for now https://plus.google.com/u/0/b/104765819602128308640/104765819602128308640/posts")

def add_campaign(request):
    if request.method == 'POST': # If the form has been submitted...
        form = CampaignForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            form.save();
            return redirect('/Force/campaigns') # Redirect after POST
    else:
        form = CampaignForm() # An unbound form

    return render(request, '/Force/AddCampaign.html', {'form': form})

def auvdeployments(request):
    latest_auvdeployment_list = auvDeployment.objects.all()
    return render_to_response('auvindex2.html', {'latest_auvdeployment_list': latest_auvdeployment_list})
   
def campaigns(request):
    latest_campaign_list = campaign.objects.all()
    return render_to_response('campaignIndex.html', {'latest_campaign_list': latest_campaign_list},context_instance=RequestContext(request))

def auvdeploymentDetail(request, auvdeployment_id):
    djf=Django.Django(geodjango="transectShape", properties=[])
    geoj = GeoJSON.GeoJSON()

    try:
        auvdeploymentObject = auvDeployment.objects.get(id=auvdeployment_id)
    except auvDeployment.DoesNotExist:
        raise  Http404

    deployment_as_geojson = geoj.encode(djf.decode([auvDeployment.objects.get(id=auvdeployment_id)]))

    return render_to_response('auvdeploymentInstance.html', {'auvdeploymentObject': auvdeploymentObject,'deployment_as_geojson':deployment_as_geojson})


def campaignDetail(request, campaign_id):

    try:
        campaignObject = campaign.objects.get(id=campaign_id)
    except campaign.DoesNotExist:
        raise  Http404

    auvdeploymentListForCampaign = auvDeployment.objects.filter(campaign=campaignObject)

    campaign_as_geojson = "test"#serializers.serialize("json", [campaign.objects.get(id=campaign_id)])
    #lets get the bounding geojson


    return render_to_response('campaignInstance.html', {'campaignObject': campaignObject, 'auvdeploymentListForCampaign':auvdeploymentListForCampaign, 'campaign_as_geojson':campaign_as_geojson})
