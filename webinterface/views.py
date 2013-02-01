# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from collection.api import CollectionResource
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import logging

#not API compliant - to be removed after the views are compliant
from Force.models import Image, Campaign, AUVDeployment, BRUVDeployment, DOVDeployment, Deployment, StereoImage, Annotation, TIDeployment, TVDeployment
from vectorformats.Formats import Django, GeoJSON
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.db.models import Max, Min
import simplejson

#account management
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

logger = logging.getLogger(__name__)

#@login_required

#front page and zones
def index(request):
    """@brief returns root catami html

    """

    #NOT API COMPLIANT
    recent_deployments = Deployment.objects.all().order_by('-id')[:3]
    random_images = Image.objects.all().order_by('?')[:9]

    styled_deployment_list = []
    image_link_list = []

    for image in random_images:
        try:
            AUVDeployment.objects.get(id=image.deployment.id)
        except:
            pass
        else:
            image_link = {"deployment_url":reverse(auvdeployments)+str(image.deployment.id),"image":image}

        try:
            TIDeployment.objects.get(id=image.deployment.id)
        except:
            pass
        else:
            image_link = {"deployment_url":reverse(tideployments)+str(image.deployment.id),"image":image}

        image_link_list.append(image_link)

    for deployment in recent_deployments:
        try:
            AUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type= "AUV Deployment"
            deployment_url = reverse(auvdeployments)+str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type= "BRUV Deployment"
            deployment_url = reverse(bruvdeployments)+str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type= "DOV Deployment"
            deployment_url =reverse(dovdeployments)+str(deployment.id)

        try:
            TIDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type= "TI Deployment"
            deployment_url = reverse(tideployments)+str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type= "TV Deployment"
            deployment_url = reverse(tvdeployments)+str(deployment.id)

        styled_deployment = {"deployment_type":deployment_type,"deployment_url":deployment_url,"deployment":deployment}
        styled_deployment_list.append(styled_deployment)

    return render_to_response('catamiPortal/index.html',
        {'styled_deployment_list':styled_deployment_list,
         'image_link_list': image_link_list},
        RequestContext(request))


# Account stuff
def logout_view(request):
    """@brief returns user to html calling the logout action

    """
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Info pages
def faq(request):
    return render_to_response('webinterface/faq.html', {}, RequestContext(request))

def contact(request):
    return render_to_response('webinterface/contact.html', {}, RequestContext(request))

def about(request):
    return render_to_response('webinterface/about.html', {}, RequestContext(request))

def howto(request):
    return render_to_response('webinterface/howto.html', {}, RequestContext(request))

# Explore pages
def explore(request):
    return render_to_response('webinterface/explore.html', {}, RequestContext(request))

# Collection pages
def collections(request):
    collection_list = CollectionResource()
    cl_my_rec = collection_list.obj_get_list(request,owner=request.user.id)
    cl_pub_rec = collection_list.obj_get_list()
    return render_to_response('webinterface/collections.html', {"my_rec_cols":cl_my_rec,"pub_rec_cols":cl_pub_rec}, RequestContext(request))

def my_collections(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list(request,owner=request.user.id)
    return render_to_response('webinterface/mycollections.html', {"collections": cl, "listname":"cl_pub_all"}, RequestContext(request))

def public_collections(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list()
    return render_to_response('webinterface/publiccollections.html', {"collections": cl, "listname":"cl_pub_all"}, RequestContext(request))

## view collection table views
#def public_collections_all(request):
#    collection_list = CollectionResource()
#    cl = collection_list.obj_get_list()
#   return render_to_response('webinterface/publiccollections.html', {"collections": cl, "listname":"cl_pub_all"}, RequestContext(request))

def view_collection(request,collection_id):
    return render_to_response('webinterface/viewcollection.html', {}, RequestContext(request))

# view collection table views
#def public_collections_all(request):
#    collection_list = CollectionResource()
#    cl = collection_list.obj_get_list()
#    return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_all"}, RequestContext(request))

#def public_collections_recent(request):
#    collection_list = CollectionResource()
#    cl = collection_list.obj_get_list()
#    return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_rec"}, RequestContext(request))

#def my_collections_all(request):
#    collection_list = CollectionResource()
#    cl = collection_list.obj_get_list(request,owner=request.user.id)
#    return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_all"}, RequestContext(request))

#def my_collections_recent(request):
#    collection_list = CollectionResource()
#    cl = collection_list.obj_get_list(request,owner=request.user.id)
#    return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_rec"}, RequestContext(request))

# collection object tasks
def delete_collection(request):
    return nil

def flip_public_collection(request):
    return nil

# Subset pages
def view_subset(request):
    return render_to_response('webinterface/viewsubset.html', {}, RequestContext(request))

def all_subsets(request):
    return render_to_response('webinterface/allsubsets.html', {}, RequestContext(request))

def my_subsets(request):
    return render_to_response('webinterface/mysubsets.html', {}, RequestContext(request))

def public_subsets(request):
    return render_to_response('webinterface/publicsubsets.html', {}, RequestContext(request))
    
# Single image pages
def image_view(request):
    return render_to_response('webinterface/imageview.html', {}, RequestContext(request))

def image_annotate(request):
    return render_to_response('webinterface/imageannotate.html', {}, RequestContext(request))

def image_edit(request):
    return render_to_response('webinterface/imageedit.html', {}, RequestContext(request))

#Force views from old view setup (NOT API COMPLIANT)
def data(request):
    return render_to_response('webinterface/Force_views/index.html', {}, RequestContext(request))

def deployments(request):
    """@brief Deployment list html for entire database

    """
    auv_deployment_list = AUVDeployment.objects.all()
    bruv_deployment_list = BRUVDeployment.objects.all()
    dov_deployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentIndex.html',
        {'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list},
        context_instance=RequestContext(request))


def deployments_map(request):
    """@brief Deployment map html for entire database

    """
    latest_deployment_list = Deployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentMap.html',
        {'latest_deployment_list': latest_deployment_list},
        context_instance=RequestContext(request))


def auvdeployments(request):
    """@brief AUV Deployment list html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/auvDeploymentIndex.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployments_map(request):
    """@brief AUV Deployment map html for entire database

    """
    latest_auvdeployment_list = AUVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/auvDeploymentMap.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployment_display(request, auvdeployment_id):
    """@brief AUV Deployment page for specifed AUV deployment

    """

    try:
        auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    except AUVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))
        #raise Http404

    return render_to_response(
        'webinterface/Force_views/auvdeployment_display.html',
        {'auvdeployment_object': auvdeployment_object},
        context_instance=RequestContext(request))


#subsamples lists of numbers and makes them suitable to be swallowed up by flot charts
def subsample_list(list):
    list_length = len(list)

    #this is used to scale down the list, so that flot isn't overwhelmed with points to render
    scale_factor = 4

    #try and pre-allocate some space in memory for the list
    #new_list = list_length/scale_factor*[None]
    new_list = []

    #iterate through points and subsample based on the scale_factor
    for i in range(0,list_length,scale_factor):
        new_list.append([i, list[i]])

    return new_list

def auvdeployment_detail(request, auvdeployment_id):
    """@brief AUV Deployment map and data plot for specifed AUV deployment

    """
    # the hard way. All columns in the geojson
    #djf=Django.Django(geodjango="transect_shape", properties=[])

    #geoj = GeoJSON.GeoJSON()
    #deployment_as_geojson = geoj.encode(djf.decode([AUVDeployment.objects.get(id=auvdeployment_id)]))

    try:
        auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    except AUVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
            'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))
        #raise Http404

    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)

    #get annotation list. Not all images have annotation
    annotated_imagelist = list()
    # for image in image_list:
    #     if(Annotation.objects.filter(image_reference=image).count() > 0):
    #         annotated_imagelist.append(image)

    #valmax = image_list.aggregate(Max('depth'))
    #valmax = image_list.aggregate(Max('depth'))
    depth_range = {'max':image_list.aggregate(Max('depth'))['depth__max'],'min':image_list.aggregate(Min('depth'))['depth__min']}
    salinity_range = {'max':image_list.aggregate(Max('salinity'))['salinity__max'],'min':image_list.aggregate(Min('salinity'))['salinity__min']}
    temperature_range = {'max':image_list.aggregate(Max('temperature'))['temperature__max'],'min':image_list.aggregate(Min('temperature'))['temperature__min']}

    #subsample these values to display in flot
    depth_data_sampled = subsample_list(image_list.values_list('depth',flat=True).order_by('id'))
    salinity_data_sampled = subsample_list(image_list.values_list('salinity',flat=True).order_by('id'))
    temperature_data_sampled = subsample_list(image_list.values_list('temperature',flat=True).order_by('id'))

    #create a data structure for our data so it can be converted to json
    #i'm not using django's model to json serialization because it is too slow
    new_image_list = list()
    for image_model in image_list:
        new_image_list.append({"depth": image_model.depth,
                               "x": image_model.image_position.x,
                               "y": image_model.image_position.y,
                               "roll": image_model.roll,
                               "pitch": image_model.pitch,
                               "yaw": image_model.yaw,
                               "altitude": image_model.altitude,
                               "temperature": image_model.temperature,
                               "left_image_reference": image_model.left_image_reference})

    new_image_list = simplejson.dumps(new_image_list, ensure_ascii=True)

    return render_to_response(
        'webinterface/Force_views/auvdeploymentDetail.html',
        {'auvdeployment_object': auvdeployment_object,
         'deployment_as_geojson': auvdeployment_object.transect_shape.geojson,
         'image_list': new_image_list,
         'annotated_imagelist': annotated_imagelist,
         'depth_data': depth_data_sampled,
         'salinity_data': salinity_data_sampled,
         'temperature_data': temperature_data_sampled,
         'depth_range': depth_range,
         'salinity_range': salinity_range,
         'temperature_range': temperature_range},
        context_instance=RequestContext(request))


def auvimage_list(request, auvdeployment_id):
    """@brief AUV image list view

    """
    try:
        auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    except AUVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))
        #raise Http404

    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)
    return render_to_response(
        'Force/auv_image_list.html',
        {'auvdeployment_object': auvdeployment_object,
        'image_list': image_list},
        context_instance=RequestContext(request))

def annotationview(request, auvdeployment_id, image_index):
    """@brief AUV annotation view

    """
    auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)

    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)
    get_index = 1
    initial_image_index = int(image_index)
    local_image_index = 0

    styled_annotation_data = list()
    #initial_image_index =local_image_index
    #get annotation list. Not all images have annotation


    if(initial_image_index == 0):
        #find first annotated image
        for image in image_list:
            local_image_index = local_image_index + 1

            if(Annotation.objects.filter(image_reference=image).count() > 0):
                return render_to_response(
                    'Force/annotationview.html',
                    {'auvdeployment_object': auvdeployment_object,
                     'image_index': local_image_index,
                     'image_index_prev': local_image_index - 1,
                     'image_index_next': local_image_index + 1,
                     'annotated_image': image,
                     'annotation_list': Annotation.objects.filter(image_reference=image)},
                    context_instance=RequestContext(request))

    for image in image_list:
        local_image_index = local_image_index + 1
        if(Annotation.objects.filter(image_reference=image).count() > 0):
            if(local_image_index > initial_image_index):

                for annotation in Annotation.objects.filter(image_reference=image):
                    text = "<p style='z-index:100; position:absolute;  color:white; font-size:12px; font-weight:normal; left:" + str(annotation.point.x * 100) + "%; top:" + str(str(annotation.point.y * 100)) + "%;'>" + annotation.code + "</p>"
                    styled_annotation_data.append(text)
                return render_to_response(
                    'webinterface/Force_views/annotationview.html',
                    {'auvdeployment_object': auvdeployment_object,
                    'image_index': local_image_index,
                     'image_index_prev': local_image_index - 1,
                     'image_index_next': local_image_index + 1,
                     'annotated_image': image,
                     'styled_annotation_data': styled_annotation_data,
                     'annotation_list': Annotation.objects.filter(image_reference=image)},
                    context_instance=RequestContext(request))

    return render_to_response(
        'webinterface/Force_views/annotationview.html',
        {'auvdeployment_object': auvdeployment_object,
        'image_notfound_index': image_index},
        context_instance=RequestContext(request))


def bruvdeployments(request):
    """@brief BRUV Deployment list html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/bruvDeploymentIndex.html',
        {'latest_bruvdeployment_list': latest_bruvdeployment_list},
        context_instance=RequestContext(request))


def bruvdeployments_map(request):
    """@brief BRUV Deployment map html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/bruvDeploymentMap.html',
        {'latest_bruvdeployment_list': latest_bruvdeployment_list},
        context_instance=RequestContext(request))


def bruvdeployment_detail(request, bruvdeployment_id):
    """@brief BRUV Deployment html for a specifed AUV deployment

    """

    try:
        bruvdeployment_object = BRUVDeployment.objects.get(id=bruvdeployment_id)
    except BRUVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'Force/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=bruvdeployment_id)

    return render_to_response(
        'Force/bruvdeploymentInstance.html',
        {'bruvdeployment_object': bruvdeployment_object,
        'deployment_as_geojson': bruvdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def dovdeployments(request):
    """@brief DOV Deployment list html for entire database

    """
    latest_dovdeployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/dovDeploymentIndex.html',
        {'latest_dovdeployment_list': latest_dovdeployment_list},
        context_instance=RequestContext(request))


def dovdeployment_detail(request, dovdeployment_id):
    """@brief DOV Deployment html for a specifed AUV deployment

    """

    try:
        dovdeployment_object = DOVDeployment.objects.get(id=dovdeployment_id)
    except DOVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=dovdeployment_id)

    return render_to_response(
        'webinterface/Force_views/tvdeploymentInstance.html',
        {'dovdeployment_object': dovdeployment_object,
        'deployment_as_geojson': dovdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def tvdeployments(request):
    """@brief TV Deployment list html for entire database

    """
    latest_tvdeployment_list = TVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/tvDeploymentIndex.html',
        {'latest_tvdeployment_list': latest_tvdeployment_list},
        context_instance=RequestContext(request))


def tvdeployment_detail(request, tvdeployment_id):
    """@brief TV Deployment html for a specifed AUV deployment

    """

    try:
        tvdeployment_object = TVDeployment.objects.get(id=tvdeployment_id)
    except TVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=tvdeployment_id)

    return render_to_response(
        'webinterface/Force_views/tvdeploymentInstance.html',
        {'tvdeployment_object': tvdeployment_object,
        'deployment_as_geojson': tvdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def tideployments(request):
    """@brief TI Deployment list html for entire database

    """
    latest_tideployment_list = TIDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/tiDeploymentIndex.html',
        {'latest_tideployment_list': latest_tideployment_list},
        context_instance=RequestContext(request))


def tideployment_detail(request, tideployment_id):
    """@brief TI Deployment html for a specifed AUV deployment

    """

    try:
        tideployment_object = TIDeployment.objects.get(id=tideployment_id)
    except TIDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=tideployment_id)

    return render_to_response(
        'Force/tideploymentInstance.html',
        {'tideployment_object': tideployment_object,
        'deployment_as_geojson': tideployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def campaigns(request):
    """@brief Campaign list html for entire database

    """
    latest_campaign_list = Campaign.objects.all()
    campaign_rects = list()

    for campaign in latest_campaign_list:
        auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign)
        bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign)
        dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign)
        if(len(auv_deployment_list) > 0):
            sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
        if(len(bruv_deployment_list) > 0):
            sm = fromstr('MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)

    return render_to_response(
        'webinterface/Force_views/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list,
        'campaign_rects': campaign_rects},
        context_instance=RequestContext(request))


def campaign_detail(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """
    try:
        campaign_object = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'webinterface/Force_views/data_missing.html', context_instance=RequestContext(request))
    campaign_rects = list()
    #djf = Django.Django(geodjango="extent", properties=[''])

    auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign_object)
    bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign_object)
    dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign_object)
    ti_deployment_list = TIDeployment.objects.filter(campaign=campaign_object)
    tv_deployment_list = TVDeployment.objects.filter(campaign=campaign_object)
    #geoj = GeoJSON.GeoJSON()
    #sm = AUVDeployment.objects.filter(transect_shape__bbcontains=pnt_wkt)
    #sm = AUVDeployment.objects.all().extent
    #sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())

    sm = ' '
    if(len(auv_deployment_list) > 0):
        sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    if(len(bruv_deployment_list) > 0):
        sm = fromstr('MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    try:
        sm_envelope = sm.envelope.geojson
    except AttributeError:
        sm_envelope = ''

    return render_to_response(
        'webinterface/Force_views/campaign_detail.html',
        {'campaign_object': campaign_object,
        'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list,
        'ti_deployment_list': ti_deployment_list,
        'tv_deployment_list': tv_deployment_list,

        'campaign_as_geojson': sm_envelope},
        context_instance=RequestContext(request))