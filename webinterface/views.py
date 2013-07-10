# Create your views here.
from django.template import RequestContext

from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import guardian
from guardian.shortcuts import get_objects_for_user
import logging

#for the geoserver proxy
from django.views.decorators.csrf import csrf_exempt
from catamidb.models import *
from django.contrib.gis.geos import fromstr
from django.db.models import Max, Min
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

import httplib2
import simplejson
import HTMLParser

logger = logging.getLogger(__name__)

def check_permission(user, permission, object):
    """
    A helper function for checking permissions on object. Need this
    because of the anonymous user.
    """

    #just make sure we get the anonymous user from the database - so we can user permissions
    if user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    return user.has_perm(permission, object)

def get_objects_for_user_wrapper(user, permission_array):
    """
    Helper function that wraps get_objects_for_user, I put this here to
    save having to obtain the anonymous user all the time.
    """
    #just make sure we get the anonymous user from the database - so we can user permissions
    if user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    return get_objects_for_user(user, permission_array)


#front page and zones
def index(request):
    """@brief returns root catami html
    """
    return render_to_response('webinterface/index.html',
                              RequestContext(request))


# Account stuff
def logout_view(request):
    """@brief returns user to html calling the logout action

    """
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# Info pages
def faq(request):
    return render_to_response('webinterface/faq.html', {},
                              RequestContext(request))


def contact(request):
    return render_to_response('webinterface/contact.html', {},
                              RequestContext(request))


def licensing(request):
    return render_to_response('webinterface/licensing.html', {},
                              RequestContext(request))


def about(request):
    return render_to_response('webinterface/about.html', {},
                              RequestContext(request))


def howto(request):
    return render_to_response('webinterface/howto.html', {},

                              RequestContext(request))


# Projects page
def projects(request):
    return render_to_response('webinterface/project-list.html', {}, RequestContext(request))


def project_view(request, project_id):
    return render_to_response('webinterface/project-view.html',
                              {"project_id": project_id,
                               'WMS_URL': settings.WMS_URL,
                               'project_WMS_layer_name': settings.WMS_PROJECTS_LAYER_NAME,
                               'annotation_set_WMS_layer_name': settings.WMS_ANNOTATIONSET_LAYER_NAME},
                              RequestContext(request))

def project_create(request):
    return render_to_response('webinterface/project-create.html',
                              {},
                              RequestContext(request))

def project_configure(request, project_id):
    return render_to_response('webinterface/project-configure.html',
                              {"project_id": project_id},
                              RequestContext(request))


def project_annotate(request, project_id):
    return render_to_response('webinterface/project-annotate.html',
                              {"project_id": project_id
                               },
                              RequestContext(request))


# Single image pages
def image_view(request):
    return render_to_response('webinterface/imageview.html', {},
                              RequestContext(request))


#Force views from old view setup (NOT API COMPLIANT)
def data(request):
    return render_to_response('webinterface/Force_views/index.html', {},
                              RequestContext(request))


def deployment_list(request):
    """@brief Deployment list html for entire database
    """
    return render_to_response(
        'webinterface/deployment-list.html',
        {'deployment_list': GenericDeployment.objects.all()},
        context_instance=RequestContext(request))


def deployment_view(request, deployment_id):
    """@brief AUV Deployment map and data plot for specifed AUV deployment

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])

    deployment_object = {}

    try:
        deployment_object = list(GenericDeployment.objects.filter(
            id=deployment_id, campaign__in=latest_campaign_list))[0]

    #if it doesn't exist or we dont have permission then go back to the main list
    except Exception:
        return deployments(request)

    return render_to_response(
        'webinterface/deployment-view.html',
        {'deployment_object': deployment_object,
         'WMS_URL': settings.WMS_URL,
         'WMS_LAYER_NAME': settings.WMS_LAYER_NAME,
         'deployment_id': deployment_object.id},
        context_instance=RequestContext(request))


@login_required
def campaigncreate(request):
    context = {}
    rcon = RequestContext(request)

    return render_to_response('webinterface/campaigncreate.html', context, rcon)


def campaigns(request):
    """@brief Campaign list html for entire database

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])  # Campaign.objects.all()
    campaign_rects = list()

    '''
    for campaign in latest_campaign_list:
        auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign)
        bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign)
        dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign)
        if len(auv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
        if len(bruv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
    '''
    return render_to_response(
        'webinterface/Force_views/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list,
         'campaign_rects': campaign_rects},
        context_instance=RequestContext(request))


def campaign_list(request):
    """@brief Campaign list html for entire database

    """

    campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])  # Campaign.objects.all()

    return render_to_response(
        'webinterface/campaign-list.html',
        {'campaign_list': campaign_list,
         'WMS_URL': settings.WMS_URL,
         'WMS_CAMPAIGNS': settings.WMS_CAMPAIGNS},
        context_instance=RequestContext(request))


def campaign_view(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """
    try:
        campaign_object = Campaign.objects.get(id=campaign_id)  
        #deployments = GenericDeployment.objects.filter(campaign=campaign_id)     
        #check for permissions
        if not check_permission(request.user, 'catamidb.view_campaign', campaign_object):
            raise Campaign.DoesNotExist
    except Campaign.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
            'webinterface/Force_views/data_missing.html',
            context_instance=RequestContext(request))
    return render_to_response(
        'webinterface/campaign-view.html',
        {'campaign_object': campaign_object, 
         'WMS_URL': settings.WMS_URL,
         'WMS_DEPLOYMENTS': settings.WMS_DEPLOYMENTS},
        context_instance=RequestContext(request))


@csrf_exempt
def proxy(request):

    url = request.GET.get('url',None)

    conn = httplib2.Http()
    if request.method == "GET":
        resp, content = conn.request(url, request.method)
        return HttpResponse(content)
    elif request.method == "POST":
        url = url
        data = request.body
        resp, content = conn.request(url, request.method, data)
        return HttpResponse(content)
