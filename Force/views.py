"""@brief Django views generation (html) for Catami data.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""

# Create your views here.
from django import forms
from django.template import RequestContext
from django.http import Http404
from django.shortcuts import render_to_response, redirect, render
from django.db.models import Max, Min
#from django.core import serializers
#from django.contrib.gis.geos import GEOSGeometry
#from django.contrib.gis.geos import *
from vectorformats.Formats import Django, GeoJSON
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from Force.models import Campaign, AUVDeployment, BRUVDeployment, DOVDeployment, Deployment, StereoImage, Annotation, TIDeployment, TVDeployment


class spatial_search_form(forms.Form):
    """@brief Simple spatial search form for Catami data

    """
    latitude = forms.FloatField(label='Latitude (decimal degrees)')
    longitude = forms.FloatField(label='Longitude (decimal degrees)')
    searchradius = forms.FloatField(label='Search Radius (km)')


def index(request):
    """@brief Root html for Catami data

    """
    context = {}

    return render_to_response(
        'Force/index.html',
        context,
        RequestContext(request))


def spatialsearch(request):
    """@brief Spatial search for Catami data

    """
    if request.method == 'POST':  # If the form has been submitted...
        form = spatial_search_form(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            deployment_points = list()
            deployment_objects = list()

            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            searchradius = form.cleaned_data['searchradius']

            geom = fromstr('POINT(%s %s)' % (longitude, latitude))
            # get deployments within distance
            auv_deployment_list = AUVDeployment.objects.filter(start_position__distance_lte=(geom, D(km=searchradius)))
            bruv_deployment_list = BRUVDeployment.objects.filter(start_position__distance_lte=(geom, D(km=searchradius)))
            dov_deployment_list = DOVDeployment.objects.filter(start_position__distance_lte=(geom, D(km=searchradius)))
            for object in auv_deployment_list:
                deployment_points.append(object.start_position.geojson)
                deployment_objects.append(object)
            for object in bruv_deployment_list:
                deployment_points.append(object.start_position.geojson)
                deployment_objects.append(object)
            for object in dov_deployment_list:
                deployment_points.append(object.start_position.geojson)
                deployment_objects.append(object)

            # make geojson for appended set
            return render_to_response('Force/spatialSearch.html', {
                          'form': form,
                          'latitude': latitude,
                          'longitude': longitude,
                          'searchradius': searchradius,
                          'deployment_points': deployment_points,
                          'deployment_objects': deployment_objects, },
                          context_instance=RequestContext(request))
    else:
        form = spatial_search_form()  # An unbound form

    return render_to_response('Force/spatialSearch.html', {
        'form': form,
    }, context_instance=RequestContext(request))


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

    try:
        auvdeployment_object = AUVDeployment.objects.get(id=auvdeployment_id)
    except AUVDeployment.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
           'Force/data_missing.html', context_instance=RequestContext(request))
        #raise Http404

    image_list = StereoImage.objects.filter(deployment=auvdeployment_id)

    #get annotation list. Not all images have annotation
    annotated_imagelist = list()
    for image in image_list:
        if(Annotation.objects.filter(image_reference=image).count() > 0):
            annotated_imagelist.append(image)

    #valmax = image_list.aggregate(Max('depth'))
    #valmax = image_list.aggregate(Max('depth'))
    depth_range = {'max':image_list.aggregate(Max('depth'))['depth__max'],'min':image_list.aggregate(Min('depth'))['depth__min']}
    salinity_range = {'max':image_list.aggregate(Max('salinity'))['salinity__max'],'min':image_list.aggregate(Min('salinity'))['salinity__min']}
    temperature_range = {'max':image_list.aggregate(Max('temperature'))['temperature__max'],'min':image_list.aggregate(Min('temperature'))['temperature__min']}



    # the easy way is to just return
    # auvdeployment_object.transect_shape.geojson
    return render_to_response(
        'Force/auvdeploymentInstance.html',
        {'auvdeployment_object': auvdeployment_object,
        'deployment_as_geojson': auvdeployment_object.transect_shape.geojson,
        'image_list': image_list,
        'annotated_imagelist': annotated_imagelist,
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
           'Force/data_missing.html', context_instance=RequestContext(request))
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
                    'Force/annotationview.html',
                    {'auvdeployment_object': auvdeployment_object,
                    'image_index': local_image_index,
                     'image_index_prev': local_image_index - 1,
                     'image_index_next': local_image_index + 1,
                     'annotated_image': image,
                     'styled_annotation_data': styled_annotation_data,
                     'annotation_list': Annotation.objects.filter(image_reference=image)},
                    context_instance=RequestContext(request))

    return render_to_response(
        'Force/annotationview.html',
        {'auvdeployment_object': auvdeployment_object,
        'image_notfound_index': image_index},
        context_instance=RequestContext(request))


def bruvdeployments(request):
    """@brief BRUV Deployment list html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'Force/bruvDeploymentIndex.html',
        {'latest_bruvdeployment_list': latest_bruvdeployment_list},
        context_instance=RequestContext(request))


def bruvdeployments_map(request):
    """@brief BRUV Deployment map html for entire database

    """
    latest_bruvdeployment_list = BRUVDeployment.objects.all()
    return render_to_response(
        'Force/bruvDeploymentMap.html',
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
        'Force/dovDeploymentIndex.html',
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
           'Force/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=dovdeployment_id)

    return render_to_response(
        'Force/tvdeploymentInstance.html',
        {'dovdeployment_object': dovdeployment_object,
        'deployment_as_geojson': dovdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def tvdeployments(request):
    """@brief TV Deployment list html for entire database

    """
    latest_tvdeployment_list = TVDeployment.objects.all()
    return render_to_response(
        'Force/tvDeploymentIndex.html',
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
           'Force/data_missing.html', context_instance=RequestContext(request))

    image_list = StereoImage.objects.filter(deployment=tvdeployment_id)

    return render_to_response(
        'Force/tvdeploymentInstance.html',
        {'tvdeployment_object': tvdeployment_object,
        'deployment_as_geojson': tvdeployment_object.start_position.geojson,
        'image_list': image_list},
        context_instance=RequestContext(request))


def tideployments(request):
    """@brief TI Deployment list html for entire database

    """
    latest_tideployment_list = TIDeployment.objects.all()
    return render_to_response(
        'Force/tiDeploymentIndex.html',
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
           'Force/data_missing.html', context_instance=RequestContext(request))

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
        'Force/campaignIndex.html',
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
           'Force/data_missing.html', context_instance=RequestContext(request))
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
        'Force/campaignInstance.html',
        {'campaign_object': campaign_object,
        'auv_deployment_list': auv_deployment_list,
        'bruv_deployment_list': bruv_deployment_list,
        'dov_deployment_list': dov_deployment_list,
        'ti_deployment_list': ti_deployment_list,
        'tv_deployment_list': tv_deployment_list,

        'campaign_as_geojson': sm_envelope},
        context_instance=RequestContext(request))
